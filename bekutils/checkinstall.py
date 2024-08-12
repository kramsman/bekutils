""" see if my package was installed into env """
import numpy as np


# GOOD
# from bekutils import bek_utils
# bek_utils.groupby_main()


# GOOD
# from bekutils.maincode import groupby_main as mn
# mn()
from bekutils import setup_loguru

logger = setup_loguru('DEBUG', 'DEBUG')
logger.info("testing")

# GOOD
from bekutils import is_number as bk1
print(f"{bk1(np.nan)=}")
print(f"{bk1('1')=}")
print(f"{bk1('A')=}")

# GOOD
import bekutils.bek_funcs as newname
print(f"{newname.is_number('A')=}")




from bekutils import is_number
print(f"{is_number('1')=}")




a=1
