# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Academic(models.Model):
    id = models.BigIntegerField()
    num_emplea = models.BigIntegerField(blank=True, null=True)
    cve_academic = models.CharField(max_length=6)
    nombres = models.CharField(max_length=50)
    apellidos = models.CharField(max_length=100)
    cve_sexo = models.CharField(max_length=9)
    cve_campus = models.CharField(max_length=3)
    cve_institu = models.CharField(max_length=3)
    cve_program = models.CharField(max_length=3)
    grado = models.CharField(max_length=12, blank=True, null=True)
    activo = models.CharField(max_length=1, blank=True, null=True)
    externo = models.CharField(max_length=1, blank=True, null=True)
    no_oficina = models.CharField(max_length=5, blank=True, null=True)
    edificio = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=60)
    extension = models.CharField(max_length=6, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'academic'


class AltaBaja(models.Model):
    id_ayb = models.BigAutoField(primary_key=True)
    cve_estud = models.BigIntegerField(blank=True, null=True)
    cve_curso = models.CharField(max_length=6, blank=True, null=True)
    nombre = models.CharField(max_length=120, blank=True, null=True)
    cve_academic = models.CharField(max_length=6, blank=True, null=True)
    nom_academic = models.CharField(max_length=50, blank=True, null=True)
    apellidos = models.CharField(max_length=100, blank=True, null=True)
    gpo_670 = models.CharField(max_length=2, blank=True, null=True)
    fech_mov = models.DateField(blank=True, null=True)
    alta_baja = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'alta_baja'


class Asistira(models.Model):
    id = models.BigAutoField(primary_key=True)
    cve_estud = models.BigIntegerField()
    cve_curso = models.CharField(max_length=6)
    gpo_670 = models.CharField(max_length=2, blank=True, null=True)
    califica = models.FloatField()
    creditos = models.IntegerField(blank=True, null=True)
    periodo = models.CharField(max_length=9)
    agno = models.IntegerField()
    observa = models.CharField(max_length=7, blank=True, null=True)
    registro = models.DateField(blank=True, null=True)
    per_vi_cur = models.CharField(max_length=9)
    ano_vi_cur = models.IntegerField()
    no_periodo = models.IntegerField()
    isevaluated = models.IntegerField(db_column='IsEvaluated', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'asistira'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Becarios(models.Model):
    cve_becaria = models.IntegerField()
    cve_estud = models.IntegerField()
    cve_campus = models.CharField(max_length=3)
    inicbeca = models.DateField()
    finabeca = models.DateField()
    cve_cona = models.IntegerField()
    tipobeca = models.CharField(max_length=11)
    vige_mes = models.IntegerField()
    agno = models.IntegerField()
    cvu = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'becarios'
        db_table_comment = 'Informacion de Becarios'


class Capcurs(models.Model):
    id = models.BigAutoField(primary_key=True)
    cve_program = models.CharField(max_length=3)
    id_catacurs = models.IntegerField()
    cve_curso = models.CharField(max_length=6)
    nombre = models.CharField(max_length=120)
    cve_academic = models.CharField(max_length=6)
    nom_academic = models.CharField(max_length=50)
    apellidos = models.CharField(max_length=100)
    participacion = models.CharField(max_length=20)
    creditos = models.IntegerField()
    aula = models.CharField(max_length=100, blank=True, null=True)
    observaciones = models.CharField(max_length=120, blank=True, null=True)
    lunes_ini = models.TimeField(blank=True, null=True)
    lunes_fin = models.TimeField(blank=True, null=True)
    martes_ini = models.TimeField(blank=True, null=True)
    martes_fin = models.TimeField(blank=True, null=True)
    miercoles_fin = models.TimeField(blank=True, null=True)
    miercoles_ini = models.TimeField(blank=True, null=True)
    jueves_ini = models.TimeField(blank=True, null=True)
    jueves_fin = models.TimeField(blank=True, null=True)
    viernes_fin = models.TimeField(blank=True, null=True)
    viernes_ini = models.TimeField(blank=True, null=True)
    periodo = models.CharField(max_length=9)
    agno = models.IntegerField(blank=True, null=True)
    lunes_inip = models.TimeField(blank=True, null=True)
    lunes_finp = models.TimeField(blank=True, null=True)
    martes_inip = models.TimeField(blank=True, null=True)
    martes_finp = models.TimeField(blank=True, null=True)
    miercoles_inip = models.TimeField(blank=True, null=True)
    miercoles_finp = models.TimeField(blank=True, null=True)
    jueves_inip = models.TimeField(blank=True, null=True)
    jueves_finp = models.TimeField(blank=True, null=True)
    viernes_inip = models.TimeField(blank=True, null=True)
    viernes_finp = models.TimeField(blank=True, null=True)
    aulap = models.TextField(blank=True, null=True)
    observacionesp = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'capcursapp'


class CapcursappCoordinaciones(models.Model):
    id = models.BigAutoField(primary_key=True)
    last_login = models.DateTimeField(blank=True, null=True)
    cve_campus = models.CharField(max_length=3)
    cve_posgrad = models.CharField(max_length=6)
    nom_posgra = models.CharField(max_length=60)
    cve_program = models.CharField(max_length=3)
    nom_program = models.CharField(max_length=50)
    username = models.CharField(unique=True, max_length=50)
    password = models.CharField(max_length=128)
    cont_veces = models.IntegerField()
    cont_final = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'capcursapp_coordinaciones'


class Catabeca(models.Model):
    id = models.IntegerField()
    cve_campus = models.CharField(max_length=3)
    cve_becaria = models.IntegerField()
    nombre = models.CharField(max_length=200)
    direccion = models.CharField(max_length=250)

    class Meta:
        managed = False
        db_table = 'catabeca'
        db_table_comment = 'Instituciones Becarias'


class Catacurs(models.Model):
    id = models.BigAutoField(primary_key=True)
    cve_campus = models.CharField(max_length=3)
    cve_program = models.CharField(max_length=3)
    cve_curso = models.CharField(max_length=6)
    gpo_670 = models.CharField(max_length=2, blank=True, null=True)
    nombre = models.CharField(max_length=120)
    credimi = models.IntegerField()
    credima = models.IntegerField()
    vigente = models.CharField(max_length=2, blank=True, null=True)
    es_tecno = models.CharField(max_length=1, blank=True, null=True)
    periodo = models.CharField(max_length=9)
    agno = models.IntegerField()
    hay_credi = models.CharField(max_length=2, blank=True, null=True)
    hay_calif = models.CharField(max_length=2, blank=True, null=True)
    tipo = models.CharField(max_length=16)
    isevaluated = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'catacurs'


class Catanaci(models.Model):
    cve_campus = models.CharField(max_length=3)
    cve_nacion = models.IntegerField()
    nombre = models.CharField(max_length=80)

    class Meta:
        managed = False
        db_table = 'catanaci'
        db_table_comment = 'Catalogo de nacionalidades'


class Coordinaciones(models.Model):
    last_login = models.DateTimeField(blank=True, null=True)
    cve_campus = models.CharField(max_length=3)
    cve_posgrad = models.CharField(max_length=6)
    nom_posgra = models.CharField(max_length=60)
    cve_program = models.CharField(max_length=3)
    nom_program = models.CharField(max_length=50)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    cont_veces = models.IntegerField()
    cont_final = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'coordinaciones'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class EstudNacion(models.Model):
    cve_estud = models.BigIntegerField(blank=True, null=True)
    cve_nacion = models.IntegerField(blank=True, null=True)
    cve_campus = models.CharField(max_length=3, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'estud_nacion'


class EstudianteConsejero(models.Model):
    id = models.BigAutoField(primary_key=True)
    cve_estud = models.BigIntegerField(blank=True, null=True)
    cve_academic = models.CharField(max_length=6, blank=True, null=True)
    registro = models.DateField(blank=True, null=True)
    agno = models.IntegerField(blank=True, null=True)
    participa = models.CharField(max_length=11, blank=True, null=True)
    orden = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'estudiante_consejero'


class Imparegu(models.Model):
    id_auto = models.AutoField(primary_key=True)
    num_emplea = models.BigIntegerField(blank=True, null=True)
    cve_academic = models.CharField(max_length=6)
    cve_curso = models.CharField(max_length=6)
    gpo_670 = models.CharField(max_length=2)
    periodo = models.CharField(max_length=9)
    agno = models.IntegerField()
    participa = models.CharField(max_length=11)
    registro = models.DateField()
    per_vi_cur = models.CharField(max_length=9)
    ano_vi_cur = models.IntegerField()
    dis_cre = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'imparegu'
        db_table_comment = 'Cursos impartidos por los profesores'


class InscripEstudian(models.Model):
    last_login = models.DateTimeField(blank=True, null=True)
    id = models.BigIntegerField()
    cve_estud = models.BigIntegerField(blank=True, null=True)
    nombres = models.CharField(max_length=50)
    apellidos = models.CharField(max_length=100)
    cve_campus = models.CharField(max_length=3)
    cve_institu = models.CharField(max_length=3)
    cve_program = models.CharField(max_length=3)
    periingr = models.CharField(max_length=9)
    fechingr = models.DateField(blank=True, null=True)
    cve_sexo = models.CharField(max_length=9)
    e_mail = models.CharField(max_length=50)
    username = models.CharField(max_length=50, blank=True, null=True)
    niveestu = models.CharField(max_length=9, blank=True, null=True)
    password = models.CharField(max_length=128)
    cont_veces = models.IntegerField()
    cont_final = models.IntegerField()
    aeta = models.IntegerField()
    consejop = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'inscrip_estudian'


class Orientador(models.Model):
    no_opcion = models.IntegerField()
    cve_academic = models.CharField(max_length=6)
    cve_estud = models.BigIntegerField()
    nombre = models.CharField(max_length=65)
    periodo = models.CharField(max_length=9)
    agno = models.IntegerField()
    f_registro = models.DateField()
    notas = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'orientador'
        db_table_comment = 'Orientadores temporales.'


class Sinsevi(models.Model):
    id_sinsevi = models.BigAutoField(primary_key=True)
    cve_estud = models.BigIntegerField(blank=True, null=True)
    id_capcurs = models.ForeignKey(Capcurs, models.DO_NOTHING, db_column='id_capcurs', blank=True, null=True)
    cve_curso = models.CharField(max_length=6, blank=True, null=True)
    nombre = models.CharField(max_length=120, blank=True, null=True)
    credimi = models.IntegerField(blank=True, null=True)
    credima = models.IntegerField(blank=True, null=True)
    cve_academic = models.CharField(max_length=6, blank=True, null=True)
    nom_academic = models.CharField(max_length=50, blank=True, null=True)
    apellidos = models.CharField(max_length=100, blank=True, null=True)
    gpo_670 = models.CharField(max_length=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sinsevi'


class SinseviEstudian(models.Model):
    last_login = models.DateTimeField(blank=True, null=True)
    id = models.BigAutoField(primary_key=True)
    cve_estud = models.BigIntegerField(blank=True, null=True)
    nombres = models.CharField(max_length=50)
    apellidos = models.CharField(max_length=100)
    cve_campus = models.CharField(max_length=3)
    cve_institu = models.CharField(max_length=3)
    cve_program = models.CharField(max_length=3)
    periingr = models.CharField(max_length=9)
    fechingr = models.DateField(blank=True, null=True)
    cve_sexo = models.CharField(max_length=9)
    e_mail = models.CharField(max_length=50)
    username = models.CharField(max_length=50, blank=True, null=True)
    aeta = models.IntegerField()
    consejop = models.IntegerField()
    password = models.CharField(max_length=128)
    niveestu = models.CharField(max_length=9, blank=True, null=True)
    cont_veces = models.IntegerField()
    cont_final = models.IntegerField()
    email_ayb = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sinsevi_estudian'
