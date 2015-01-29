node[:crons].each_pair do |cronname, options|
    cron cronname do
      minute options[:minute] || "*"
      hour options[:hour] || "*"
      day options[:day] || "*"
      month options[:month] || "*"
      weekday options[:weekday] || "*"
      command options[:command]
      user options[:user] || node[:apps_user]
    end
end

