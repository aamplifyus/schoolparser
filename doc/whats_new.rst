:orphan:

.. _whats_new:


What's new?
===========

Here we list a changelog of EZTrack.

.. contents:: Contents
   :local:
   :depth: 3

.. currentmodule:: eztrack

.. _current:

Current
-------

.. _changes_0_1:

Version 0.1
-----------

Changelog
~~~~~~~~~

- Add support for eegio and a corresponding refactoring of API: :func:`fit` by `Adam Li`_ (`#21 <https://github.com/adam2392/eztrack/pull/21>`_)
- Add refactoring of the UI endpoints API by `Patrick Myers`_ (`#23 <https://github.com/adam2392/eztrack/pull/23>`_)
- Add preprocess utility functions in :code:`eztrack.base.utils.preprocess_utils` by `Adam Li`_ (`#26 <https://github.com/adam2392/eztrack/pull/26>`_)
- Add BIDS layout testing data to `data/bids_layout` by `Adam Li`_ (`#32 <https://github.com/adam2392/eztrack/pull/32>`_)
- Cleanup pytest fixtures to be more BIDS compliant by `Adam Li`_ (`#41 <https://github.com/adam2392/eztrack/pull/41>`_)
- Fragility analysis saves directly into derivatives folder now by `Adam Li`_ (`#41 <https://github.com/adam2392/eztrack/pull/41>`_)
- Removing unnecessary inputs and dependencies (mainly eegio) from the CLI by  `Patrick Myers`_ (`#42 <https://github.com/adam2392/eztrack/pull/42>`_)
- Validation checks to raw data and fragility algorithm output by `Adam Li`_ (`#43 <https://github.com/adam2392/eztrack/pull/43>`_)
- Adding enumerations to hardcoded data variables in config by `Adam Li`_ (`#54 <https://github.com/adam2392/eztrack/pull/54>`_)
- Appending scans.tsv original filenames and participant metadata to corresponding json/tsv files by `Adam Li`_ (`#51 <https://github.com/adam2392/eztrack/pull/51>`_)
- Refactor visualization API to be more usable and limit the amount of public functions by `Adam Li`_ (`#61 <https://github.com/adam2392/eztrack/pull/61>`_)
- Fixing validation checks to determine if any 'bad' channels are left in `Raw` data structure by `Adam Li`_ (`#57 <https://github.com/adam2392/eztrack/pull/57>`_)
- Changed parallelization to use joblib instead of multiprocessing by `Adam Li`_ (`#57 <https://github.com/adam2392/eztrack/pull/57>`_)
- Allow fragility analysis run in `pipeline` to save results in npz file immediately, without using `RunMergeModel` by `Adam Li`_ (`#57 <https://github.com/adam2392/eztrack/pull/57>`_)
- Map events data structure :code:`eztrack/base/utils/annotations` from EEG raw data files to fragility window samples by `Adam Li`_ (`#57 <https://github.com/adam2392/eztrack/pull/57>`_)
- Add circleci and appveyor to repository by `Adam Li`_ (`#57 <https://github.com/adam2392/eztrack/pull/57>`_)
- Add unit tests to satisfy FDA requirements `Patrick Myers`_ (`#70 <https://github.com/adam2392/eztrack/pull/70>`_)
- Fixing date portion of anonymization to have dates before 1925 `Patrick Myers`_ (`#70 <https://github.com/adam2392/eztrack/pull/70>`_)
- Added tqdm progress bar to :func:`RunFragModel.runparallel` by `Adam Li`_ (`#75 <https://github.com/adam2392/eztrack/pull/75>`_)
- Fixing heatmap formatting by dynamically adjusting figure size and setting font size by `Patrick Myers`_ (`#84 <https://github.com/adam2392/eztrack/pull/84>`_)
- Add more user-friendly output and simplified code in :func:`cli.metadata` and :func:`cli.pat_summary`, to allow for user-feedback on incorrect inputs by `Adam Li`_ (`#81 <https://github.com/adam2392/eztrack/pull/81>`_)
- Added CLI function to view bad channels and label channels as bad or remove bad label by `Patrick Myers`_ (`#87 <https://github.com/adam2392/eztrack/pull/87>`_)
- Added notch/bp unit tests for filtering from mne-python by `Adam Li`_ (`#81 <https://github.com/adam2392/eztrack/pull/81>`_)
- Added verification of bad channels, input data format, output data format and output file format by `Adam Li`_ (`#82 <https://github.com/adam2392/eztrack/pull/82>`_)
- Added environment variable setting of BIDSROOT, SOURCEDATA_DIR and DERIVATIVES_DIR in CLI by `Adam Li`_ (`#82 <https://github.com/adam2392/eztrack/pull/82>`_)
- Removed analysis, added plotting to the end of run, and added customizability to plotting in CLI by `Patrick Myers`_ (`#100 <https://github.com/adam2392/eztrack/pull/100>`_)
- Added useful help statements in CLI by `Patrick Myers`_ (`#100 <https://github.com/adam2392/eztrack/pull/100>`_)
- Added logs, timers, and error counts to CLI and backend by `Patrick Myers`_ (`#102 <https://github.com/adam2392/eztrack/pull/102>`_)
- Removed error tracebacks from console and sent to logs via customized errors by `Patrick Myers`_ (`#102 <https://github.com/adam2392/eztrack/pull/102>`_)
- Added filtering functionality to metadata function in CLI by `Patrick Myers`_ (`#102 <https://github.com/adam2392/eztrack/pull/102>`_)
- Added color options to help commands in CLI by `Patrick Myers`_ (`#106 <https://github.com/adam2392/eztrack/pull/106>`_)
- Added hidden directory to store log files by `Patrick Myers`_ (`#112 <https://github.com/adam2392/eztrack/pull/112>`_)

Bug
~~~

- Fix running of fragility analysis in :code:`eztrack.runfrag` by `Adam Li`_ (`#26 <https://github.com/adam2392/eztrack/pull/26>`_)
- Fix access to patient dictionary via enumeration in :code:`eztrack/base/config/config` `Adam Li`_ (`#57 <https://github.com/adam2392/eztrack/pull/57>`_)
- Fix bugs in annotations `_find_sz_samples` and `_find_clinonset_samples` when none are found, or more then 1 are found by `Adam Li`_ (`#75 <https://github.com/adam2392/eztrack/pull/75>`_)
- Fix bug in extension checking in :func:`write_to_bids` by `Adam Li`_ (`#75 <https://github.com/adam2392/eztrack/pull/75>`_)
- Fix CLI to adhere to changes in :func:`analyze_data`, such as `reference` tag, and removed unused CLI code by `Adam Li`_ (`#78 <https://github.com/adam2392/eztrack/pull/78>`_)
- Fix :func:`_get_prob_chs`, to trim any blank " " space characters in the user electrode_layout Excel sheet by `Adam Li`_ (`#81 <https://github.com/adam2392/eztrack/pull/81>`_)
- Fix :func:`eztrack.base.validate.validate_raw_metadata` to allow None in subject_info for Info data structures by `Adam Li`_ (`#106 <https://github.com/adam2392/eztrack/pull/106>`_)

API
~~~

- Add scalp EEG preprocessing pipeline in :code:`eztrack.preprocess_eeg` by `Adam Li`_ (`#26 <https://github.com/adam2392/eztrack/pull/26>`_)
- Add an explicit pipeline for converting datasets into BIDS given a filepath in :code:`eztrack.convert_bids` by `Adam Li`_ (`#26 <https://github.com/adam2392/eztrack/pull/26>`_)

Authors
~~~~~~~

People who contributed to this release (in alphabetical order):

* Adam Li
* Patrick Myers

.. _Adam Li: https://github.com/adam2392
.. _Patrick Myers: https://github.com/pmyers16
