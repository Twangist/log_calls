#####[Preliminaries](#Preliminaries)
* [Version](#Version)
* [Dependencies and requirements](#Dependencies)
* [Installation](#Installation)
* [Running the Tests](#Testing)
* [Credits](#Credits)
#####[Basic Usage](#Basic-usage)
* [The *enabled* parameter](#enabled-parameter)
* [The *args_sep* parameter](#args_sep-parameter)
* [The *log_args* parameter](#log_args-parameter)
* [The *log_retval* parameter](#log_retval-parameter)
* [The *log_exit* parameter](#log_exit-parameter)
* [The *log_call_numbers* parameter](#log_call_numbers-parameter)
* [The *log_elapsed* parameter](#log_elapsed-parameter)
* [The *indent* parameter](#indent-parameter)
* [The *prefix* parameter](#prefix-parameter)
* [The *file* parameter](#file-parameter)
* [The remaining parameters](#The-remaining-parameters) ([logger](#logger-parameter), [loglevel](#loglevel-parameter), [record_history](#stats.record_history-parameter), [max_history](#stats.max_history-parameter))
#####[Using loggers](#Logging)
* [The *logger* parameter](#logger-parameter)
* [The *loglevel* parameter](#loglevel-parameter)
#####[Call Chains](#Call-chains)
* [Another *indent* example](#indent-parameter-another)
* [Call chains and inner functions](#Call-chains-inner-functions)
* [Call chains and log_call_numbers](#Call-chains-log_call_numbers)
* [Indentation and call numbers with recursion](#recursion-example)
#####[Dynamic control of settings using the log_calls_settings attribute](#Dynamic-control-log_calls_settings)
* [The problem](#problem)
* [Solutions](#solutions)
* [The *log_calls_settings* attribute](#log_calls_settings)
* [The mapping interface and the attribute interface to settings](#mapping-interface)
* [The *update()*, *as_OrderedDict()* and *as_dict()* methods](#update-as_etc)
#####[Dynamic control of settings with indirect values](#Indirect-values)
* [Controlling format 'from above'](#format-from-above)
  * [Controlling indentation 'from above'](#indent-from-above)
* [Enabling with *int*s rather than *bool*s](#enabling-with-ints)
* [Using `log_calls_settings` to set indirect values](#log_call_settings-indirect)
#####[More on using loggers](#More-on-using-loggers)
* [Indirect values for the *logger* parameter](#indirect-logger)
* [Test of indirect *loglevel*](#indirect-loglevel)
* [A realistic example – multiple handlers with different loglevels](#More-on-logging-realistic-example)
#####[A metaclass example](#A-metaclass-example)
#####[Call history and statistics](#call-history-and-statistics)
* [The *stats* attribute and *its* attributes](#stats-attribute)
* [The *stats.num_calls_logged* attribute](#stats.num_calls_logged)
* [The *stats.num_calls_total* attribute](#stats.num_calls_total)
* [The *stats.elapsed_secs_logged* attribute](#elapsed_secs_logged)
* [The *record_history* parameter](#stats.record_history-parameter)
* [The *max_history* parameter](#stats.max_history-parameter)
* [The *stats.call_history* attribute](#stats.call_history)
* [The *stats.call_history_as_csv* attribute](#stats.call_history_as_csv)
* [The *stats.clear_history()* method](#stats.clear_history)
#####[Appendix – Keyword Parameters Reference](#KeywordParametersReference)