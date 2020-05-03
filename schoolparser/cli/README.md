# EZTRACK CLI
Command line tool to run eztrack

## Installation

From the EZTrack root folder, run 

~~~
   make install-cli
~~~


## Metadata

Displays the metadata for all or a subset of the patients in the EZTrack server

Syntax:

~~~
    ez metadata [arguments] [--options]
~~~

Arguments include:
- toggle\_options (Any boolean operator from the available metadata fields)

Options include:
- display\_cols (Boolean value to just display the available fields, default = False)

Example:

~~~
    ez metadata 'age>40' 'sex=M'
~~~
This will filter to only show male patients over 40 years old

## Patient Summary

Displays the information about the snapshots for a certain patient

Syntax:

~~~
    ez pat-summary [--options]
~~~

Options include:
- subject_id (The id of the patient you want to see snapshots of. Default is all, which will just call the metadata function)

Example:

~~~
    ez pat-summary --patid='01'
~~~
This will display the snapshot information for pat01


## Run

Adds the desired file to the pipeline manager's (airflow) queue to be run

Syntax:

~~~
    ez run [--options]
~~~

Options include:
- subject_id (The id of the patient to be analyzed)
- session_id (The id of the session, default is 'seizure')
- task_id (What was occurring during the recording, default is 'monitor')
- acquisition_id (The type of recording, one of 'ecog', 'eeg', or 'seeg')
- run_id (The number identifier of the run)
- output_path (The path where results should be saved. Default is bids_layout/derivatives)

Example:

~~~
   ez run --subject_id='pt1' --acquisition_id='ecog' --run_id='01'
~~~

## Plot

Create a heatmap from the output of a fragility run

Syntax:

~~~
    ez plot [--options]
~~~

Options include:
- subject_id (The id of the patient to be analyzed)
- session_id (The id of the session, default is 'seizure')
- task_id (What was occurring during the recording, default is 'monitor')
- acquisition_id (The type of recording, one of 'ecog', 'eeg', or 'seeg')
- run_id (The number identifier of the run)
- channels (The list of channel names, default finds the channel names from the raw file)
- output_path (The path where results should be saved. Default is bids_layout)
- colorblind (A boolean value whether to plot using a cmap without green and red)

Example:

~~~
   ez plot --subject_id='0005' --acquisition_id='ecog' --run_id='01' --colorblind=True
~~~

## CLI Flow

A reasonable flow to analyze a new EEG snapshot would be:

~~~
    # Look at the metadata for all of the patients and grab the correct patid
    ez metadata
    # Check information about this snapshot
    ez pat-summary --patid='01'
    # Run the fragility algorithm
    ez run --subject_id='0005' --acquisition_id='ecog' --run_id='01'
    # Plot the results of the fragility run
    ez plot --subject_id='0005' --acquisition_id='ecog' --run_id='01' --colorblind=True
~~~
