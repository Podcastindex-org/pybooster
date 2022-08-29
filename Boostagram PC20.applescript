on run
	set theMessageDialog to display dialog "Enter Boostagram Message for PC2.0" default answer "" with icon note buttons {"Cancel", "Continue"} default button "Continue"
	set theMessage to text returned of theMessageDialog
	set theNode to "03ae9f91a0cb8ff43840e3c322c4c61f019d8c1c3cea15a25cfc425ac605e61a4a"
	set theShowName to "Podcasting 2.0"
	set theURL to "http://mp3s.nashownotes.com/pc20rss.xml"
	set theFeedID to 920666
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