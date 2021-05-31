# Q&A. 

### How to update a function to aero board?
1. Create a command folder in <b>HSI/commands/</b> with naming convenction Delimiter-separated words which are all smaller case and hyphen between keywords. For example, "TimeOfFlighCommand" => "time-of-flight-command".
2. Add a class function in the created folder with naming convention in CamelCase. Like, "TimeOfFlightCommand". 
3. Finally, update <i>_my_self_singelton_command_registry</I> in function <i>initializeCommandRegistry</I> in HSIMaster.py. 
4. Update protocol document with the new function protocol. 

### How to make a function?
1. Take examples functions from commands in the <b>HSI/commands/</b> folders. 
2. Update protocol document with the new function protocol. 

### How to start python code when boot up?
1. In Ubuntu, open "start application". 
2. Create a startup program, name the program and enter the command as *gnome-terminal -- bash -c "sudo python3 /home/hsi/HSI/HSIMaster.py; exec bash"*
