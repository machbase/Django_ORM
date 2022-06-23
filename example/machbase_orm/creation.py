"""
Written by Yeony.kim at 2021-11

create database의 기능이 완벽하게 지원되지 않기 때문에,
본 database를 생성하고 제거하는 테스트는 수행하지 않고 넘어가도록 각각 테스트 하는 로직은 모두 주석처리 하였음
"""

from django.db.backends.base.creation import BaseDatabaseCreation

from django.apps import apps
from django.conf import settings

TEST_DATABASE_PREFIX = 'django_test_'


class DatabaseCreation(BaseDatabaseCreation):
    """
        Encapsulate backend-specific differences pertaining to creation and
        destruction of the test database.
        """

    def create_test_db(self, verbosity=1, autoclobber=False, serialize=True, keepdb=False):
        """
        Create a test database, prompting the user for confirmation if the
        database already exists. Return the name of the test database created.
        """
        # Don't import django.core.management if it isn't needed.
        from django.core.management import call_command

        test_database_name = self._get_test_db_name()

        if verbosity >= 1:
            action = 'Creating Test Not Implemented'

            self.log(action)

        # We could skip this call if keepdb is True, but we instead
        # give it the keepdb param. This is to handle the case
        # where the test DB doesn't exist, in which case we need to
        # create it, then just not destroy it. If we instead skip
        # this, we will get an exception.
        self._create_test_db(verbosity, autoclobber, keepdb)

        # self.connection.close()
        # settings.DATABASES[self.connection.alias]["NAME"] = test_database_name
        # self.connection.settings_dict["NAME"] = test_database_name
        # database의 이름을 임시로 생성한 이름으로 변경하여 설정에 할당하는 로직

        try:
            if self.connection.settings_dict['TEST']['MIGRATE'] is False:
                # Disable migrations for all apps.
                old_migration_modules = settings.MIGRATION_MODULES
                settings.MIGRATION_MODULES = {
                    app.label: None
                    for app in apps.get_app_configs()
                }
            # We report migrate messages at one level lower than that
            # requested. This ensures we don't get flooded with messages during
            # testing (unless you really ask to be flooded).
            # call_command(
            #     'migrate',
            #     verbosity=max(verbosity - 1, 0),
            #     interactive=False,
            #     database=self.connection.alias,
            #     run_syncdb=True,
            # )
            # db가 변경된 사항을 반영하기 위한 migrate작업을 요청하는 로직
        finally:
            if self.connection.settings_dict['TEST']['MIGRATE'] is False:
                settings.MIGRATION_MODULES = old_migration_modules

        # We then serialize the current state of the database into a string
        # and store it on the connection. This slightly horrific process is so people
        # who are testing on databases without transactions or who are using
        # a TransactionTestCase still get a clean database on every test run.

        # if serialize:
        #     self.connection._test_serialized_contents = self.serialize_db_to_string() # _test_serialized_contents 필드의 정확한 위치를 파악하지 못하였음
        # call_command('createcachetable', database=self.connection.alias)

        # Ensure a connection for the side effect of initializing the test database.
        self.connection.ensure_connection()

        # if os.environ.get('RUNNING_DJANGOS_TEST_SUITE') == 'true':
        #     self.mark_expected_failures_and_skips()

        return test_database_name

    # def serialize_db_to_string(self):
    #     """
    #     Serialize all data in the database into a JSON string.
    #     Designed only for test runner usage; will not handle large
    #     amounts of data.
    #     """
    #
    #     # Iteratively return every object for all models to serialize.
    #     def get_objects():
    #         from django.db.migrations.loader import MigrationLoader
    #         loader = MigrationLoader(self.connection)
    #         for app_config in apps.get_app_configs():
    #             if (
    #                     app_config.models_module is not None and
    #                     app_config.label in loader.migrated_apps and
    #                     app_config.name not in settings.TEST_NON_SERIALIZED_APPS
    #             ):
    #                 for model in app_config.get_models():
    #                     if (
    #                             model._meta.can_migrate(self.connection) and
    #                             router.allow_migrate_model(self.connection.alias, model)
    #                     ):
    #                         queryset = model._base_manager.using(
    #                             self.connection.alias,
    #                         ).order_by(model._meta.pk.name)
    #                         yield from queryset.iterator()
    #
    #     # Serialize to a string
    #     out = StringIO()
    #     serializers.serialize("json", get_objects(), indent=None, stream=out)
    #     return out.getvalue()

    # def deserialize_db_from_string(self, data):
    #     """
    #     Reload the database with data from a string generated by
    #     the serialize_db_to_string() method.
    #     """
    #     data = StringIO(data)
    #     table_names = set()
    #     # Load data in a transaction to handle forward references and cycles.
    #     with atomic(using=self.connection.alias):
    #         # Disable constraint checks, because some databases (MySQL) doesn't
    #         # support deferred checks.
    #         with self.connection.constraint_checks_disabled():
    #             for obj in serializers.deserialize('json', data, using=self.connection.alias):
    #                 obj.save()
    #                 table_names.add(obj.object.__class__._meta.db_table)
    #         # Manually check for any invalid keys that might have been added,
    #         # because constraint checks were disabled.
    #         self.connection.check_constraints(table_names=table_names)

    def _get_test_db_name(self):
        """
        Internal implementation - return the name of the test DB that will be
        created. Only useful when called from create_test_db() and
        _create_test_db() and when no external munging is done with the 'NAME'
        settings.
        """
        if self.connection.settings_dict['TEST']['NAME']:
            return self.connection.settings_dict['TEST']['NAME']
        return TEST_DATABASE_PREFIX + self.connection.settings_dict['NAME']

    def _execute_create_test_db(self, cursor, parameters, keepdb=False):
        pass
        # cursor.execute('CREATE DATABASE %(dbname)s %(suffix)s' % parameters)
        # create test db 는 현재 구현되어 있지 않음

    def _create_test_db(self, verbosity, autoclobber, keepdb=False):
        """
        Internal implementation - create the test db tables.
        """
        test_database_name = self._get_test_db_name()
        test_db_params = {
            'dbname': self.connection.ops.quote_name(test_database_name),
            'suffix': self.sql_table_creation_suffix(),
        }
        # Create the test database and connect to it.
        with self._nodb_cursor() as cursor:
            try:
                pass
                # self._execute_create_test_db(cursor, test_db_params, keepdb)
                # create database에 대한 로직이 담겨있는 부분
            except Exception as e:
                # if we want to keep the db, then no need to do any of the below,
                # just return and skip it all.
                if keepdb:
                    return test_database_name

                # self.log('Got an error creating the test database: %s' % e)
                if not autoclobber:
                    # confirm = input(
                    #     "Type 'yes' if you would like to try deleting the test "
                    #     "database '%s', or 'no' to cancel: " % test_database_name)
                    confirm = 'yes'
                    # DB를 지워도 되는지 여부를 keepdb가 false로 설정되어 있기 때문에,
                    # test 를 위해서 사용자에게 database를 지워도 되는지 한번더 묻는 코드
                if autoclobber or confirm == 'yes':
                    try:
                        pass
                        # if verbosity >= 1:
                        #     self.log('Destroying old test database for alias %s...' % (
                        #         self._get_database_display_str(verbosity, test_database_name),
                        #     ))
                        # cursor.execute('DROP DATABASE %(dbname)s' % test_db_params)
                        # self._execute_create_test_db(cursor, test_db_params, keepdb)
                        # 실제 database를 지우는 로직

                    except Exception as e:
                        pass
                        # self.log('Got an error recreating the test database: %s' % e)
                        # sys.exit(2)
                        # 에러가 났을 때 에러 log를 남기고 프로세스 종료 하는 로직

                else:
                    pass
                    # self.log('Tests cancelled.')
                    # sys.exit(1)
                    # database 설정이 keepdb가 아니나, 기존의 database를 제거하지 않는 경우, 테스트를 진행하지 않고 종료

        return test_database_name

    def clone_test_db(self, suffix, verbosity=1, autoclobber=False, keepdb=False):
        """
        Clone a test database.
        """
        source_database_name = self.connection.settings_dict['NAME']

        if verbosity >= 1:
            action = 'Cloning test database Test Not Implemented'
            self.log(action)

        # We could skip this call if keepdb is True, but we instead
        # give it the keepdb param. See create_test_db for details.
        self._clone_test_db(suffix, verbosity, keepdb)

    def get_test_db_clone_settings(self, suffix):
        """
        Return a modified connection settings dict for the n-th clone of a DB.
        """
        # When this function is called, the test database has been created
        # already and its name has been copied to settings_dict['NAME'] so
        # we don't need to call _get_test_db_name.
        orig_settings_dict = self.connection.settings_dict
        return {**orig_settings_dict, 'NAME': '{}_{}'.format(orig_settings_dict['NAME'], suffix)}

    def _clone_test_db(self, suffix, verbosity, keepdb=False):
        """
        Internal implementation - duplicate the test db tables.
        """
        pass
        # raise NotImplementedError(
        #     "The database backend doesn't support cloning databases. "
        #     "Disable the option to run tests in parallel processes.")

    def destroy_test_db(self, old_database_name=None, verbosity=1, keepdb=False, suffix=None):
        """
        Destroy a test database, prompting the user for confirmation if the
        database already exists.
        """
        # self.connection.close()
        if suffix is None:
            test_database_name = self.connection.settings_dict['NAME']
        else:
            test_database_name = self.get_test_db_clone_settings(suffix)['NAME']

        if verbosity >= 1:
            action = 'Destroying Test Not Implemented'
            self.log(action)

        # if we want to preserve the database
        # skip the actual destroying piece.
        if not keepdb:
            self._destroy_test_db(test_database_name, verbosity)

        # Restore the original database name
        if old_database_name is not None:
            settings.DATABASES[self.connection.alias]["NAME"] = old_database_name
            self.connection.settings_dict["NAME"] = old_database_name

    def _destroy_test_db(self, test_database_name, verbosity):
        """
        Internal implementation - remove the test db tables.
        """
        # Remove the test database to clean up after
        # ourselves. Connect to the previous database (not the test database)
        # to do so, because it's not allowed to delete a database while being
        # connected to it.
        pass
        # with self._nodb_cursor() as cursor:
        #     cursor.execute("DROP DATABASE %s"
        #                    % self.connection.ops.quote_name(test_database_name))

    def mark_expected_failures_and_skips(self):
        """
        Mark tests in Django's test suite which are expected failures on this
        database and test which should be skipped on this database.
        설정된 테스트 케이스에 대해서 실패시 skip 설정이 추가된 test case에 대한 marking logic
        """
        # for test_name in self.connection.features.django_test_expected_failures:
        #     test_case_name, _, test_method_name = test_name.rpartition('.')
        #     test_app = test_name.split('.')[0]
        #     # Importing a test app that isn't installed raises RuntimeError.
        #     if test_app in settings.INSTALLED_APPS:
        #         test_case = import_string(test_case_name)
        #         test_method = getattr(test_case, test_method_name)
        #         setattr(test_case, test_method_name, expectedFailure(test_method))
        # for reason, tests in self.connection.features.django_test_skips.items():
        #     for test_name in tests:
        #         test_case_name, _, test_method_name = test_name.rpartition('.')
        #         test_app = test_name.split('.')[0]
        #         # Importing a test app that isn't installed raises RuntimeError.
        #         if test_app in settings.INSTALLED_APPS:
        #             test_case = import_string(test_case_name)
        #             test_method = getattr(test_case, test_method_name)
        #             setattr(test_case, test_method_name, skip(reason)(test_method))

    def sql_table_creation_suffix(self):
        """
        SQL to append to the end of the test table creation statements.
        """
        return ''

    def test_db_signature(self):
        """
        Return a tuple with elements of self.connection.settings_dict (a
        DATABASES setting value) that uniquely identify a database
        accordingly to the RDBMS particularities.
        """
        settings_dict = self.connection.settings_dict
        return (
            settings_dict['HOST'],
            settings_dict['PORT'],
            settings_dict['ENGINE'],
            self._get_test_db_name(),
        )