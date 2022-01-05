from functools import partial

from simulator import get_session as gs

# noinspection PyUnresolvedReferences
from simulator import close_session


get_session = partial(gs, nb_agents=1)

open_session = get_session


if __name__ == "__main__":

    open_session()
