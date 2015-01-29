package "pgpool2" do
    :upgrade
end

cookbook_file "/etc/pgpool2/pgpool.conf" do
  source "pgpool/pgpool.conf"
  user "postgres"
  group "postgres"
  mode 0640
end

cookbook_file "/etc/postgresql/9.1/main/pg_hba.conf" do
  source "pgpool/pg_hba.conf"
  user "postgres"
  group "postgres"
  mode 0640
end

node[:apps].each do |app|
    script "Set pgpool password for #{app[:name]}" do
      interpreter "bash"
      user "root"
      group "root"
      code <<-EOH
        pg_md5 '#{app[:db_password]}' | awk '{print "#{app[:db_user]}:"$1}' >> /etc/pgpool2/pcp.conf;
      EOH
    end
end

script "Set ownership of pgpool conf directory" do
  interpreter "bash"
  user "root"
  group "root"
  code <<-EOH
    chown postgres -R /etc/pgpool2;
  EOH
end

script "Create pgpool pid directory" do
  interpreter "bash"
  user "root"
  group "root"
  code <<-EOH
    mkdir /var/run/pgpool;
    chown postgres /var/run/pgpool;
    chgrp postgres /var/run/pgpool;
  EOH
end

script "Restart postgres" do
  interpreter "bash"
  user "root"
  group "root"
  code <<-EOH
    service postgresql restart
  EOH
end

script "Restart pgpool" do
  interpreter "bash"
  user "root"
  group "root"
  code <<-EOH
    service pgpool2 restart
  EOH
end
