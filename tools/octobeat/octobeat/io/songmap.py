from pathlib import Path

from octobeat.models.songmap import SongMap


def read_songmap(path: Path) -> SongMap:
    """
    Read a SongMap from disk.
    """

    return SongMap.model_validate_json(
        path.expanduser().read_text(encoding="utf-8")
    )

def songmap_to_json(songmap: SongMap) -> str:
    """
    Serialize a SongMap into a formatted JSON document.
    """

    return songmap.model_dump_json(
        indent=2,
        by_alias=True,
        exclude_none=True,
    )


def write_songmap(songmap: SongMap, destination: Path) -> None:
    """
    Write a SongMap to disk.
    """

    destination = destination.expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)

    destination.write_text(
        songmap_to_json(songmap) + "\n",
        encoding="utf-8",
    )