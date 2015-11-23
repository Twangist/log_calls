__author__ = 'BTO'

#------------------------------------------------------------------------------
##~ PROFILE
#------------------------------------------------------------------------------
# from collections import OrderedDict
#
# class time_block():
#     def __init__(self, label):
#         self.label = label
#         self.elapsed_list1 = [0.0]  # self.elapsed_list1[0] replaced with elapsed time
#
#     def __enter__(self):
#         self.start = time.perf_counter()
#         # self.elapsed_list1 becomes the value of foo in
#         #       with time_block(lbl) as foo: ...
#         # (see __exit__).
#         # Caller/user accesses elapsed time via foo[0]
#         return self.elapsed_list1
#
#     def __exit__(self, exc_ty, exc_val, exc_tb):
#         end = time.perf_counter()
#         self.elapsed_list1[0] = end - self.start
#         # print('{}: {}'.format(self.label, end - self.start))
# END PROFILE

# Usage:

# Initialize:
            ##~ PROFILE
            # self.profile__ = OrderedDict((
            #     ('setup_stackframe_hack', []),
            #     ('up_to__not_enabled_call', []),
            #     ('setup_context_init', []),
            #     ('setup_context_inspect_bind', []),
            #     ('setup_context_post_bind', []),
            #     ('setup_context_kwargs_dicts', []),
            #     ('pre_call_handlers', []),
            #     ('post_call_handlers', []),
            # ))
            # END PROFILE

# time groups of lines e.g., here, within a function [f_log_calls_wrapper]:
                ##~ PROFILE
                #~ with time_block('setup_stackframe_hack') as profile__setup_stackframe_hack:
                #      <code>

# collect
                ##~ PROFILE
                # self.profile__['setup_stackframe_hack'].extend(profile__setup_stackframe_hack)
                # self.profile__['up_to__not_enabled_call'].extend(profile__up_to__not_enabled_call)
                # self.profile__['setup_context_init'].extend(profile__setup_context_init)
                # self.profile__['setup_context_inspect_bind'].extend(profile__setup_context_inspect_bind)
                # self.profile__['setup_context_post_bind'].extend(profile__setup_context_post_bind)
                # self.profile__['setup_context_kwargs_dicts'].extend(profile__setup_context_kwargs_dicts)
                # self.profile__['pre_call_handlers'].extend(profile__pre_call_handlers)
                # self.profile__['post_call_handlers'].extend(profile__post_call_handlers)
                #~ END PROFILE

# For log_calls, we had:
            ##~ PROFILE
            # setattr(
            #     _deco_base_f_wrapper_,
            #     'profile__',
            #     self.profile__
            # )
            # END PROFILE

