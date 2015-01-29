define :virtualenv, :action => :create, :owner => "root", :group => "root", :mode => 0755, :packages => {} do
    path = params[:path] ? params[:path] : params[:name]
    if params[:action] == :create
        # Manage the directory.
        directory path do
            owner params[:owner]
            group params[:group]
            mode params[:mode]
        end
        execute "create-virtualenv-#{path}" do
            user params[:owner]
            group params[:group]
            command "virtualenv --no-site-packages #{path}"
            not_if "test -f #{path}/bin/python"
        end
        params[:packages].each_pair do |package, version|
            pip = "#{path}/bin/pip"
            execute "install-#{package}-#{path}" do
                user params[:owner]
                group params[:group]
                command "#{pip} install #{package}==#{version}"
                not_if "[ `#{pip} freeze | grep #{package} | cut -d'=' -f3` = '#{version}' ]"
            end
        end
    elsif params[:action] == :delete
        directory path do
            action :delete
            recursive true
        end
    end
end
