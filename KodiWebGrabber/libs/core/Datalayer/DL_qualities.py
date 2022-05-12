from ..databaseHelper import databaseHelper


class DL_qualities:

    @staticmethod
    def getItem(con, quality):
        query = 'SELECT quality_id FROM qualities WHERE name = ?;'
        quality_id = databaseHelper.executeScalar(con, query, (quality, ))
        if quality_id is None:
            tag_id = 0
        return quality_id

    @staticmethod
    def insertItem(con, quality):
        statement = 'INSERT INTO qualities (name) VALUES (?);'

        return databaseHelper.executeNonQuery(con, statement, (quality, ))

    @staticmethod
    def getOrInsertItem(con, quality):
        _quality_id = DL_qualities.getItem(con, quality)
        if _quality_id == 0:
            _, _quality_id = DL_qualities.insertItem(con, quality)

        return _quality_id
