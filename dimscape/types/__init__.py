from registrar import CellTypeRegistrar
from media import VideoCell, AudioCell, ImageCell
from text import TextCell
from system import ProgCell, SystemWarnCell
from clone import CloneCell

# system types get registered here for now, fixes cycle between
# registrar and registrees
CellTypeRegistrar.get().register("video", VideoCell, system=False)
CellTypeRegistrar.get().register("warn", SystemWarnCell, system=True)
CellTypeRegistrar.get().register("prog", ProgCell, system=False)
CellTypeRegistrar.get().register("text", TextCell, system=False)
