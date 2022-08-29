on run
	set theMessageDialog to display dialog "Enter Boostagram Message" default answer "" with icon note buttons {"Cancel", "Continue"} default button "Continue"
	set theNodeDialog to display dialog "Enter Node Address" default answer "" with icon note buttons {"Cancel", "Continue"} default button "Continue"
	set theShowNameDialog to display dialog "Enter Show Name" default answer "" with icon note buttons {"Cancel", "Continue"} default button "Continue"
	set theURLDialog to display dialog "Enter RSS Feed URL" default answer "" with icon note buttons {"Cancel", "Continue"} default button "Continue"
	set theFeedIDDialog to display dialog "Enter RSS Feed ID" default answer "" with icon note buttons {"Cancel", "Continue"} default button "Continue"
	set theMessage to text returned of theMessageDialog
	set theNode to text returned of theNodeDialog
	set theShowName to text returned of theShowNameDialog
	set theURL to text returned of theURLDialog
	set theFeedID to text returned of theFeedIDDialog
	if application "Terminal" is running then
		tell application "Terminal"
			do script ("/usr/local/bin/python3 /Users/johnchidgey/Documents/pybooster/main.py -m '" & theMessage & "' -n '" & theNode & "' -s '" & theShowName & "' -u '" & theURL & "' -i " & theFeedID)
			set current settings of selected tab of window 1 to settings set "Homebrew"
		end tell
	else
		tell application "Terminal"
			do script "/usr/local/bin/python3 /Users/johnchidgey/Documents/pybooster/main.py -m '" & theMessage & "' -n '" & theNode & "' -s '" & theShowName & "' -u '" & theURL & "' -i " & theFeedID in window 1
			set current settings of selected tab of window 1 to settings set "Homebrew"
		end tell
	end if
end run