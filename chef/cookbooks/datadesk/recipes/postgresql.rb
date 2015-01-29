# Intended to work on Ubuntu 12.04

package "binutils" do
    :upgrade
end

package "gdal-bin" do
    :upgrade
end

package "libproj-dev" do
    :upgrade
end

package "postgresql-9.1-postgis" do
    :upgrade
end

package "postgresql-server-dev-9.1" do
    :upgrade
end

package "python-psycopg2" do
    :upgrade
end

cookbook_file "/tmp/create_postgis_template.sh" do
  source "postgresql/create_postgis_template.sh"
  mode 0640
  owner "postgres"
  group "postgres"
end

script "create-postgis-template" do
  interpreter "bash"
  user "postgres"
  cwd "/tmp"
  code <<-EOH
  source ./create_postgis_template.sh
  EOH
end
