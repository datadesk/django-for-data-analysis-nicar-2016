# Install munin and some extras
package "munin" do
    :upgrade
end

package "munin-node" do
    :upgrade
end

package "munin-plugins-extra" do
    :upgrade
end

# Do the basic config for the master
template "/etc/munin/munin.conf" do
  source "munin/munin.conf.erb"
  mode "777"
  owner "root"
  group "root"
  variables({
     :name => node[:munin_name]
  })
end

# Do the basic config for the node
template "/etc/munin/munin-node.conf" do
  source "munin/munin-node.conf.erb"
  mode "777"
  owner "root"
  group "root"
  variables({
     :name => node[:munin_name],
     :munin_master_ips => node[:munin_master_ips]
  })
end

script "Zero out munin apache.conf" do
  interpreter "bash"
  user "root"
  group "root"
  code <<-EOH
    echo "#nothing to see here" > /etc/munin/apache.conf
  EOH
end

# Install the framework for Python plugins
script "Install PyMunin" do
  interpreter "bash"
  user "root"
  group "root"
  code <<-EOH
    pip install PyMunin;
  EOH
end

# A postgresql plugin, first the conf...
template "/etc/munin/plugin-conf.d/pgstats" do
  source "munin/pgstats.erb"
  owner "root"
  group "root"
  variables({
     :munin_db_user => node[:munin_db_user],
     :munin_db_name => node[:munin_db_name],
     :munin_include_db_list => node[:munin_include_db_list]
  })
end

# A postgresql plugin
script "Install postgresql adaptor for python" do
  interpreter "bash"
  user "root"
  group "root"
  code <<-EOH
    pip install psycopg2;
  EOH
end

script "Install pgstats for PyMunin" do
  interpreter "bash"
  user "root"
  group "root"
  code <<-EOH
    ln -s /usr/share/munin/plugins/pgstats /etc/munin/plugins/pgstats
  EOH
  not_if do
    File.exists?("/etc/munin/plugins/pgstats")
  end
end

# Make sure we have the correct Apache plugins
script "Install Apache2 plugins" do
  interpreter "bash"
  user "root"
  group "root"
  code <<-EOH
    ln -s /usr/share/munin/plugins/apache_accesses /etc/munin/plugins/apache_accesses
    ln -s /usr/share/munin/plugins/apache_processes /etc/munin/plugins/apache_processes
    ln -s /usr/share/munin/plugins/apachestats /etc/munin/plugins/apachestats
    ln -s /usr/share/munin/plugins/apache_volume /etc/munin/plugins/apache_volume
  EOH
  not_if do
    File.exists?("/etc/munin/plugins/apachestats")
  end
end

# A memcached plugin
script "Install memcachedstats for PyMunin" do
  interpreter "bash"
  user "root"
  group "root"
  code <<-EOH
    ln -s /usr/share/munin/plugins/memcachedstats /etc/munin/plugins/memcachedstats
  EOH
  not_if do
    File.exists?("/etc/munin/plugins/memcachedstats")
  end
end

# Varnish plugin
script "Install varnishstats for PyMunin" do
  interpreter "bash"
  user "root"
  group "root"
  code <<-EOH
    ln -s /usr/share/munin/plugins/varnishstats /etc/munin/plugins/varnishstats
  EOH
  not_if do
    File.exists?("/etc/munin/plugins/varnishstats")
  end
end

script "Restart Munin" do
  interpreter "bash"
  user "root"
  group "root"
  code <<-EOH
    service munin-node restart;
    service apache2 restart;
  EOH
end
