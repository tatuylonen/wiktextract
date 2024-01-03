from typing import (
    Union,
)


WordData = dict[str, Union[
                           str,
                           int,
                           list[str],
                           list[list[str]],
                           "WordData",
                           list["WordData"]
                        ]
                ]
