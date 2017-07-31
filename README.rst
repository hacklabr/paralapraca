.. image:: https://badge.waffle.io/hacklabr/paralapraca.png?label=ready&title=Ready 
 :target: https://waffle.io/hacklabr/paralapraca
 :alt: 'Stories in Ready'
=============================
Paralapracá
=============================

Development (with Docker)
--------------------------
Clone the development versions of timtec, django-discussion and paralapraca
::
    git clone https://github.com/hacklabr/timtec.git
    git clone https://github.com/hacklabr/django-discussion.git
    git clone https://github.com/hacklabr/paralapraca.git

Switch timtec to its paralapraca compatible version
::
    cd timtec
    git checkout paralapraca

Go back to your main folder and copy some docker files (this proccess will improve in the future)
::
    cp paralapraca/Dockerfile-dev Dockerfile-dev
    cp paralapraca/docker-compose.yml docker-compose.yml
    cp paralapraca/docker-compose-update.sh docker-compose-update.sh

Now, you're ready to get your stack up and running
::
    docker-compose up


Aditional notes
~~~~~~~~~~~~~~~~~
If you would like to have interactive control for debuging in your server log (pdb or ipdb support), you must activate the stack with the following command
::
    docker-compose run --service-ports --rm web


Deploy a production database on your local environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Put the dump file given to you by the Hacklab/ team on the installation directory.

Copy the file to the database container (do it while the application runs).
::
    docker cp dump.psqlc <directory_name>_db_1:/tmp

Now, enter in the container and run the restore command.
::
    docker exec -it <directory_name>_db_1 bash
    # you're inside the container now
    su postgres
    pg_restore -O -c -x -n public -d timtec /tmp/dump.psqlc

Credits
---------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
