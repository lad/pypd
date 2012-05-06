import testutils


def pytest_generate_tests(metafunc):
    # Separate test files define their own funcarg functions decorated
    # with testutils.parameterize(). That populates testutils.args_params
    # with the arg name and list of parameter names. These are passed to
    # metafunc.parametrize() to generate separate test runs of the
    # test function using each of the generated argument sets in turn.
    for arg, params in testutils.args_params:
        if arg in metafunc.funcargnames:
            metafunc.parametrize(arg, params, indirect=True)
