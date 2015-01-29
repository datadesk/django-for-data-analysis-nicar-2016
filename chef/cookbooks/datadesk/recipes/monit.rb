package "monit" do
    :upgrade
end

template "/etc/monit/monitrc" do
  source "monit/monitrc.erb"
  mode "777"
  owner "root"
  group "root"
  variables({
     :monit_test_ip => node[:monit_test_ip]
  })
end

script "Set monit's startup variable" do
  interpreter "bash"
  user "root"
  group "root"
  code <<-EOH
    echo "startup=1" > /etc/default/monit
  EOH
end

script "Restart monit" do
  interpreter "bash"
  user "root"
  group "root"
  code <<-EOH
    service monit restart
  EOH
end
