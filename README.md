
# ASCoT: The Application for Sanger Confirmatory Sequencing


[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/) 

[![Issues](https://img.shields.io/github/issues/025georgialynny/ASCoT)](https://github.com/025georgialynny/ASCoT/issues)

A Graphical Software Interface for Management of Confirmatory Sequencing in Genomic Medicine. ASCoT is a standalone and containerized cross-platform software package for sample management particularly tailored for user-friendliness.





## Authors

- [Georgia Smith](https://www.github.com/GeorgiaLynny)[^1]
- Elizabeth Gilliland[^1]
- [Chris Gignoux](https://www.gignouxlab.org/)[^1]
- [Kristy Crooks](https://medschool.cuanschutz.edu/pathology/department-of-pathology-our-services/cmoco/our-team/Crooks-Kristy-UCD6000076708)[^1]


[^1]:  Colorado Center for Personalized Medicine,University of Colorado Anschutz Medical Campus 
## Installation

ASCoT is a web application built on python3 flask. An installation file is created for debian distributions in file `install.sh` using `apt`. Super-User privileges are required. Prior install of python3 is required. 

This was built using a debian [Docker Dev Environment](https://docs.docker.com/desktop/dev-environments/).  

```bash
  sudo bash install.sh
```
    
The installation file installs pip3, MySQL, and all dependencies. It also creates database `flaskdb` with user/password `ascot/asco`. These credentials can be changed in `install.sh`, note that they must be changed in `app/__init__.py` as well. 
## Run Locally

Clone the project

```bash
  git clone https://github.com/025georgialynny/ASCoT
```

Go to the project directory

```bash
  cd ASCoT
```

Install dependencies

```bash
  sudo bash install.sh
```

Start the server

```bash
  ./flaskrun.sh
```

Access on browser at https://localhost:5000. Note the default login (username/pw) is root/root on install. 

## File Tree
```
.
├── config_default.py - Flask Configuration
├── flaskrun.sh - Run Application
├── install.sh - Install Application
├── make_exe.sh - Create Executable from PyInstaller
├── mysql_install.sh - Install MySql and Initialize DB
├── requirements.txt - Python Requirements List
├── app - Main Application File 
│   ├── __init__.py - Application Init File
│   ├── build_data.py - Setup Data based on original data file (app/data/samples/sample_version/sample_data.csv)
│   ├── build_items.py - HTML Item Builder (To be replaced by WTForms Functions)
│   ├── data - Data Files (To be replaced with MySQL Database)
│   │   ├── samples
│   │   │   └── RGC_trial_RoR_042522
│   │   │       ├── approvals.csv
│   │   │       ├── logs.csv
│   │   │       ├── plate_overview.csv
│   │   │       ├── plate_primers.csv
│   │   │       ├── plate_wells.csv
│   │   │       ├── primer_list.csv
│   │   │       ├── sample_data.csv
│   │   │       └── samples_overview.csv
│   ├── database_outline.json - Outline to Initialize Database
│   ├── deidentify.py - Deidentify daa stored in (app/data/original_data)
│   ├── forms.py - Form Classes for ese with WTForms
│   ├── main_data.json - Define data attributes for use with build_items.py
│   ├── pages.json - Format of pages 
│   ├── site_class.py - All site functions (save, create tables, etc)
│   ├── tables.json - Format of tables 
│   ├── static - Resources including bootstrap, jQuery, and custom javascript and stylesheets
│   │   ├── resources
│   │   │   ├── bootstrap
│   │   │   │   ├── bootstrap-5.1.3-directories
│   │   │   │   |
│   │   │   │   |
│   │   │   ├── custom
│   │   │   │   ├── general_custom.js
│   │   │   │   ├── table_filter.js
│   │   │   └── style.css
│   │   └── signin.css
│   ├── templates - Flask Templates
│   │   ├── base.html - Base Template including Header
│   │   └── public - All templates 
│   │       ├── build_plate.html
│   │       ├── construction.html
│   │       ├── design_plate.html
│   │       ├── index.html
│   │       ├── login.html
│   │       ├── new_plate.html
│   │       ├── output.html
│   │       ├── plate_organize.html
│   │       ├── plate_report.html
│   │       ├── plate_report_old.html
│   │       ├── primer_list.html
│   │       ├── queues.html
│   │       ├── sequenced_plate.html
│   │       ├── settings.html
│   │       ├── settings_admin.html
│   │       ├── signup.html
│   │       ├── table_view.html
│   │       ├── user_mgmt.html
│   │       └── view_datacsv.html
│   └── views.py - Main Flask File

```

## License

[MIT](https://choosealicense.com/licenses/mit/)

