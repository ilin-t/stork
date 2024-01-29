import re

from benchmarks.filter_pipelines import filter_pipeline
from src.ast.import_visitor import ImportVisitor
from src.log_modules import util
from benchmarks.run import filter_folders, list_files_paths, filter_python_files

class RepositoryMarker():
    def __init__(self, repository):
        self.dpfs = {'numpy': ['load', 'loadtxt', 'genfromtxt', 'fromfile'],
                     'pandas': ['read_table', 'read_csv', 'read_pickle', 'read_excel', 'Excel_file', 'read_json',
                                'read_html',
                                'read_xml', 'read_hdf', 'HDFStore', 'read_feather', 'read_parquet', 'read_orc',
                                'read_sas',
                                'read_spss', 'read_sql_table', 'read_sql', 'read_sql_query', 'read_gbq', 'read_stata'],
                     'cudf': ['read_csv', 'read_text', 'read_json', 'read_parquet', 'read_orc', 'read_hdf',
                              'read_feather',
                              'read_avro'],
                     'pyspark': ['csv', 'format', 'jdbc', 'json', 'load', 'option', 'options', 'orc', 'parquet',
                                 'schema', 'table',
                                 'text', 'read_table', 'read_delta', 'read_parquet', 'read_orc',
                                 'read_spark_io', 'read_csv', 'read_clipboard', 'read_excel', 'read_json', 'read_html',
                                 'read_sql_table', 'read_sql_query', 'read_sql'],
                     'dask': ['read_text', 'read_avro', 'read_csv', 'read_parquet', 'read_hdf', 'read_orc', 'read_json',
                              'read_sql_table', 'read_sql_query', 'read_sql', 'read_table', 'read_fwf'],
                     'arrow': ['OSFile', 'memory_map', 'BufferReader', 'read', 'open_file',
                               'csv.open_csv,' 'csv.read_csv',
                               'feather.read_feather', 'feather.read_table', 'json.ReadOptions',
                               'json.read_json', 'parquet.ParquetDataset', 'parquet.ParquetFile', 'parquet.read_table',
                               'parquet.read_metadata', 'parquet.read_pandas', 'parquet.read_schema', 'orc.ORCFile',
                               'orc.ORCWriter', 'orc.read_table', 'orc.write_table'],
                     'duckdb': ['read_csv', 'read_parquet', 'sql', 'json'],
                     'modin': ['read_table', 'read_csv', 'read_pickle', 'read_excel', 'Excel_file', 'read_json',
                               'read_html', 'read_xml', 'read_hdf', 'HDFStore', 'read_feather',
                               'read_parquet', 'read_orc', 'read_sas', 'read_spss', 'read_sql_table', 'read_sql',
                               'read_sql_query',
                               'read_gbq', 'read_stata'],
                     'polars': ['read_csv', 'read_csv_batched', 'scan_csv', 'read_ipc', 'read_ipc_stream', 'scan_ipc',
                                'read_parquet', 'scan_parquet', 'read_database',
                                'read_database_uri', 'read_json', 'read_ndjson', 'scan_ndjson', 'read_avro',
                                'read_excel',
                                'scan_iceberg', 'scan_delta', 'read_delta', 'scan_pyarrow_dataset'],
                     'datatable': ['iread', 'fread']}
        self.mlfs = {'scikit_learn': ['datasets'],
                     'tensorflow': ['data', 'datasets'],
                     'torch': ['data', 'datasets'],
                     'keras': ['datasets', 'image_dataset_from_directory', 'timeseries_dataset_from_array',
                               'text_dataset_from_directory', 'audio_dataset_from_directory']
                     }

        self.repository = repository
        self.pipelines = []
        self.flagged_pipelines_library = []
        self.flagged_pipelines_python = []
        self.flagged_repository_library = False
        self.flagged_repository_python = False

    def traverse_folders(self, path, project_logger, error_logger, data_read_pipelines_lib, data_read_pipelines_py):
        folders = filter_folders(path)
        files = list_files_paths(path)
        py_files = filter_python_files(files)

        if py_files:
            project_logger.info(f"Folder: {path}, executing the following python files:")
            for py_file in py_files:
                project_logger.info(f"\t {py_file}")
            # print(f"Repository {path} has the following python files: \n {py_files}")
            self.flag_repository(file_list=py_files, project_logger=project_logger,
                                 data_read_pipelines_lib=data_read_pipelines_lib,
                                 data_read_pipelines_py=data_read_pipelines_py)

        if folders:
            for folder in folders:
                self.traverse_folders(path=folder, project_logger=project_logger, error_logger=error_logger,
                                      data_read_pipelines_lib=data_read_pipelines_lib,
                                      data_read_pipelines_py=data_read_pipelines_py)

        return 0

    def flag_repository(self, file_list, project_logger, data_read_pipelines_lib, data_read_pipelines_py):
        for py_file in file_list:
            if not filter_pipeline(input_pipeline=py_file):
                print(f"pipeline not executable: {py_file}")
                continue
            else:
                self.flag_pipeline(py_file, project_logger, data_read_pipelines_lib=data_read_pipelines_lib,
                                   data_read_pipelines_py=data_read_pipelines_py)

    def flag_pipeline(self, pipeline, project_logger, data_read_pipelines_lib, data_read_pipelines_py):
        try:
            imp_vis = ImportVisitor()
            tree = util.getAst(pipeline=pipeline)

            imp_vis.visit(tree)
            # print(f"Pipeline {pipeline} contains the following libraries: {imp_vis.imports}")
            dpfs_libraries = self.filter_libraries(pipeline=pipeline, library_list=imp_vis.imports,
                                                   flagged_list=self.flagged_pipelines_library, flagged_log=project_logger,
                                                   log_of_pipelines=data_read_pipelines_lib)

            flagged_lib, calls_lib, flagged_py, calls_py = self.scan_compare(pipeline=pipeline,
                                                                             library_list=dpfs_libraries,
                                                                             data_read_pipelines_lib=data_read_pipelines_lib,
                                                                             data_read_pipelines_py=data_read_pipelines_py)

            if flagged_lib:
                self.flagged_pipelines_library.append(pipeline)
                project_logger.info(f"Pipeline {pipeline} has called {dpfs_libraries}, in total {calls_lib} times.")
                self.flagged_repository_library = True

            if flagged_py:
                self.flagged_pipelines_python.append(pipeline)
                project_logger.info(f"Pipeline {pipeline} has ingested data through Python, in total {calls_py} times.")
                self.flagged_repository_python = True
        except (OSError, SyntaxError, TypeError, KeyError, ValueError, NameError) as e:
            print(e)
        # print(f"Pipeline {pipeline}: {imp_vis.imports}")

    def filter_libraries(self, pipeline, library_list, flagged_log, flagged_list, log_of_pipelines):
        try:
            found_libraries = []
            method_calls = []
            for library in library_list:
                # print(f"library {library} has values: {library.values()}")
                if "import_library" in library.keys():
                    if library["import_library"] in self.dpfs.keys():
                        print(
                            f"Library {library['import_library']} was found in pipeline {pipeline} as {library['asname']}. Checking file looking for method calls.")
                        found_libraries.append(library)
                        flagged_list.append(pipeline)
                elif "import_method" in library.keys():
                    if library["from"] in self.dpfs.keys():
                        # print(f"Library {library['from']} was found in {pipeline}. Inspecting imported packages.")
                        for method in library["import_method"]:
                            if method in list(self.dpfs.values())[1]:
                                flagged_log.info(f"Pipeline {pipeline} contains {method}, data reading is checked")
                                # print(f"Pipeline {pipeline} contains {method}, data reading is checked")
                                method_calls.append({"from": library["from"], "import_method": method})
                                log_of_pipelines.info(pipeline)
            if found_libraries:
                return found_libraries
            elif method_calls:
                return method_calls
            else:
                return []
        except (OSError, SyntaxError, TypeError, KeyError, ValueError, NameError) as e:
            print(e)


    def scan_compare(self, pipeline, library_list, data_read_pipelines_lib, data_read_pipelines_py):
        try:
            flagged_pipeline_library = False
            flagged_pipeline_python = False
            method_calls_library = 0
            method_calls_python = 0
            with open(pipeline, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if " open(" in line:
                        match = re.search(r'(?<=[\'\"])[xabt+]*r[xabt+]*(?=[\'\"])', line)
                        if match:
                            print(f"Data was read in native Python in {pipeline} in the following line: {line}")
                            flagged_pipeline_python = True
                            method_calls_python += 1
                        else:
                            print(f"Open file interface not in read mode.")
                        continue
                    else:
                        for library in library_list:
                            if "import_library" in library.keys():
                                # print(f"Library {library}")
                                # print(f"Library list {library_list}")
                                # print(f"Library method: {library['import_library']}")
                                for method in self.dpfs[library['import_library']]:
                                    if f"{library['asname']}.{method}(" in line:
                                        print(
                                            f"Method {method} called in {pipeline} in the following line number: {lines.index(line)}. Method call: {line}")
                                        flagged_pipeline_library = True
                                        method_calls_library += 1
                                        break
                                continue
                            elif "import_method" in library.keys():
                                for method in self.dpfs[library['from']]:
                                    print(f"Method: {method}, dpfs library: {self.dpfs[library['from']]}")
                                    print(f"line to check: {line}")
                                    if f"{method}(" in line:
                                        print(f"{method} Detected.")
                                        print(
                                            f"Method {method} called in {pipeline} in the following line number: {lines.index(line)}. Method call: {line}")
                                        flagged_pipeline_library = True
                                        method_calls_library += 1
                                        break
                                continue
                if flagged_pipeline_library:
                    data_read_pipelines_lib.info(pipeline)
                    self.flagged_pipelines_library.append(pipeline)
                if flagged_pipeline_python:
                    data_read_pipelines_py.info(pipeline)
                    self.flagged_pipelines_python.append(pipeline)
                print(f"{flagged_pipeline_library}, number of method calls: {method_calls_library}")
                print(f"{flagged_pipeline_python}, number of python open calls: {method_calls_python}")

            f.close()
            return flagged_pipeline_library, method_calls_library, flagged_pipeline_python, method_calls_python
        except (OSError, SyntaxError, TypeError, KeyError, ValueError, NameError) as e:
            print(e)