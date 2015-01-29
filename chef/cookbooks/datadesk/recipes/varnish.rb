# Install Varnish
package "varnish" do
    :upgrade
end

# The boot config
cookbook_file "/etc/default/varnish" do
  source "varnish/varnish"
  mode 0640
end

# The rules that regulate how varnish works
template "/etc/varnish/default.vcl" do
  source "varnish/default.vcl.erb"
  mode 0640
  variables({
     :apache_port => node[:apache_port],
     :varnish_whitelist => node[:varnish_whitelist],
     :varnish_ttl => node[:varnish_ttl],
     :varnish_health_url => node[:varnish_health_url],
     :varnish_no_cache_urls => node[:varnish_no_cache_urls]
  })
end

script "Restart apache" do
  interpreter "bash"
  user "root"
  group "root"
  code <<-EOH
    service apache2 restart
  EOH
end

script "Restart varnish" do
  interpreter "bash"
  user "root"
  group "root"
  code <<-EOH
    service varnish restart
  EOH
end
