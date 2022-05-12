from ..databaseHelper import databaseHelper


class DL_itemTags:

    @staticmethod
    def getItem(con, tag):
        query = 'SELECT tag_id FROM item_tags WHERE name = ?;'
        tag_id = databaseHelper.executeScalar(con, query, (tag, ))
        if tag_id is None:
            tag_id = 0
        return tag_id

    @staticmethod
    def insertItem(con, tag):
        statement = 'INSERT INTO item_tags (name) VALUES (?);'

        return databaseHelper.executeNonQuery(con, statement, (tag, ))

    @staticmethod
    def getOrInsertItem(con, tag):
        _tag_id = DL_itemTags.getItem(con, tag)
        if _tag_id == 0:
            _, _tag_id = DL_itemTags.insertItem(con, tag)

        return _tag_id
