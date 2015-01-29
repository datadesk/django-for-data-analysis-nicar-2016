runit_service 'riemann-health' do
  options :host => node['riemann']['server']
end

service 'riemann-health' do
  supports :restart => true
  action [:start]
end

runit_service 'riemann-munin' do
  options :host => node['riemann']['server']
end

service 'riemann-munin' do
  supports :restart => true
  action [:start]
end

gem_package 'riemann-tools' do
  action :install
  notifies :restart, resources(:service => 'riemann-health')
  notifies :restart, resources(:service => 'riemann-munin')
end

# This will set the hostname for us
script "Change hostname" do
  interpreter "bash"
  user "root"
  group "root"
  code <<-EOH
    echo "#{node['riemann']['hostname']}" > /etc/hostname && hostname #{node['riemann']['hostname']}
  EOH
end

template "/etc/hosts" do
  source "hosts.erb"
  mode "777"
  owner "root"
  group "root"
  variables({
     :node => node
  })
end
