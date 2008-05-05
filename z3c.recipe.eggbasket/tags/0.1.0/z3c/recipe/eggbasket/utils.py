import tempfile
import shutil


def install_distributions(distributions, target_dir, links=[]):
    from zc.buildout.easy_install import install
    from zc.buildout.easy_install import MissingDistribution
    try:
        empty_index = tempfile.mkdtemp()

        try:
            install(distributions, target_dir, newest=False,
                    links=links, index='file://' + empty_index)
        except MissingDistribution:
            return False
        else:
            return True
    finally:
        shutil.rmtree(empty_index)


def distributions_are_installed_in_dir(distributions, target_dir):
    # Check if the required distributions are installed.  We do this
    # by trying to install the distributions in the target dir and
    # letting easy_install only look inside that same target dir while
    # doing that.
    result = install_distributions(distributions, target_dir,
                                   links=[target_dir])
    return result
