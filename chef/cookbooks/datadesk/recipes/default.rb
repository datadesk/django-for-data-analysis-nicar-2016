# Fix the locale
execute "create-locale" do
  command %Q{
    locale-gen en_US.UTF-8
  }
end

execute "set-locale" do
  command %Q{
    update-locale LANG=en_US.UTF-8
  }
end

# Load any base system wide packages
node[:base_packages].each do |pkg|
    package pkg do
        :upgrade
    end
end

# Loop through the user list, create the user, load the authorized_keys
# and mint a bash_profile
node[:users].each_pair do |username, info|
    group username do
       gid info[:id] 
    end

    user username do 
        comment info[:full_name]
        uid info[:id]
        gid info[:id]
        shell info[:disabled] ? "/sbin/nologin" : "/bin/bash"
        supports :manage_home => true
        home "/home/#{username}"
    end

    directory "/home/#{username}/.ssh" do
        owner username
        group username
        mode 0700
    end

    cookbook_file "/home/#{username}/.ssh/authorized_keys" do
      source "users/authorized_keys"
      mode 0640
      owner username
      group username
    end

    cookbook_file "/home/#{username}/.bash_profile" do
        source "users/bash_profile"
        owner username
        group username
        mode 0755
    end

end

# Set the user groups
node[:groups].each_pair do |name, info|
    group name do
        gid info[:gid]
        members info[:members]
    end
end

# Load the authorized keys for the root user
directory "/root/.ssh" do
    owner "root"
    group "root"
    mode 0700
end

cookbook_file "/root/.ssh/authorized_keys" do
  source "users/authorized_keys"
  mode 0640
  owner "root"
  group "root"
end

# Load the SSH keys
cookbook_file "/root/.ssh/id_rsa" do
  source "users/id_rsa"
  mode 0600
  owner "root"
  group "root"
end

cookbook_file "/root/.ssh/id_rsa.pub" do
  source "users/id_rsa.pub"
  mode 0644
  owner "root"
  group "root"
end

template "/etc/sudoers" do
  source "users/sudoers.erb"
  mode 0440
  owner "root"
  group "root"
  variables({
     :apps_user => node[:apps_user]
  })
end

script "Fix libfreetype.so" do
  interpreter "bash"
  user "root"
  group "root"
  code <<-EOH
    ln -s /usr/lib/`uname -i`-linux-gnu/libfreetype.so /usr/lib/
  EOH
  not_if do
    File.exists?("/usr/lib/libfreetype.so")
  end
end

script "Fix libz.so" do
  interpreter "bash"
  user "root"
  group "root"
  code <<-EOH
    ln -s /usr/lib/`uname -i`-linux-gnu/libz.so /usr/lib/
  EOH
  not_if do
    File.exists?("/usr/lib/libz.so")
  end
end

script "Fix libjpeg.so" do
  interpreter "bash"
  user "root"
  group "root"
  code <<-EOH
    ln -s /usr/lib/`uname -i`-linux-gnu/libjpeg.so /usr/lib/
  EOH
  not_if do
    File.exists?("/usr/lib/libjpeg.so")
  end
end

