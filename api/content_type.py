from telethon.tl.types import Photo, Document, MessageMediaPhoto, MessageMediaDocument


def create_union(*iterables) -> set:
    union = set()
    for it in iterables:
        union.update(it) if hasattr(it, '__iter__') else union.add(it)
    return union


manga = type('Manga', tuple(), {})
photo = {Photo, MessageMediaPhoto}
video = {Document, MessageMediaDocument}
all_types = create_union(manga, photo, video)
