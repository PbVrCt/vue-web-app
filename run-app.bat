REM Si se necesita cambiar este script a otra carpeta
REM Quitar comentario en las lineas 4 y 5 y Adaptar disco y carpeta
REM --
REM C:
REM cd C:\Proyectos\Taludes
REM --
set FLASK_APP=app.py
venv\Scripts\flask run --host=0.0.0.0 --with-threads