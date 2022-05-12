from ..databaseHelper import databaseHelper


class DL_subitemTags:

    @staticmethod
    def getItem(con, tag):
        query = 'SELECT tag_id FROM subitem_tags WHERE name = ?;'
        tag_id = databaseHelper.executeScalar(con, query, (tag, ))
        if tag_id is None:
            tag_id = 0
        return tag_id

    @staticmethod
    def insertItem(con, tag):
        statement = 'INSERT INTO subitem_tags (name) VALUES (?);'

        return databaseHelper.executeNonQuery(con, statement, (tag, ))

    @staticmethod
    def getOrInsertItem(con, tag):
        _tag_id = DL_subitemTags.getItem(con, tag)
        if _tag_id == 0:
            _, _tag_id = DL_subitemTags.insertItem(con, tag)

        return _tag_id
