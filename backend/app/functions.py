#!/usr/bin/python3

#################################################################################################################################################
#                                                    CLASSES CONTAINING ALL THE APP FUNCTIONS                                                  #
#################################################################################################################################################


class DB:
    def __init__(self, Config):
        from math import floor
        from os import getcwd
        from os.path import join
        from json import loads, dumps, dump
        from datetime import timedelta, datetime, timezone
        from pymongo import MongoClient, errors, ReturnDocument
        from urllib import parse
        from urllib.request import urlopen
        from bson.objectid import ObjectId

        self.Config = Config
        self.getcwd = getcwd
        self.join = join
        self.floor = floor
        self.loads = loads
        self.dumps = dumps
        self.dump = dump
        self.datetime = datetime
        self.ObjectId = ObjectId
        self.server = Config.DB_SERVER
        self.port = int(Config.DB_PORT)

        # These can be blank in Case A (no-auth local MongoDB).
        # Keeping them here so the class doesn’t break if you later enable auth.
        self.username = parse.quote_plus(Config.DB_USERNAME) if Config.DB_USERNAME else ""
        self.password = parse.quote_plus(Config.DB_PASSWORD) if Config.DB_PASSWORD else ""

        self.remoteMongo = MongoClient
        self.ReturnDocument = ReturnDocument
        self.PyMongoError = errors.PyMongoError
        self.BulkWriteError = errors.BulkWriteError
        self.tls = False  # MUST SET TO TRUE IN PRODUCTION

    def __del__(self):
        # Delete class instance to free resources
        pass

    ####################
    # LAB 2 DATABASE UTIL FUNCTIONS
    ####################

    def addUpdate(self, data):
        """INSERT SENSOR UPDATE INTO ELET2415.climo (Case A: no-auth local MongoDB)"""
        try:
            # No username/password (because your MongoDB allows mongodb://localhost:27017)
            remotedb = self.remoteMongo(
                "mongodb://%s:%s" % (self.server, self.port),
                tls=self.tls,
            )
            remotedb.ELET2415.climo.insert_one(data)
        except Exception as e:
            msg = str(e)
            if "duplicate" not in msg:
                print("addUpdate error", msg)
            return False
        else:
            return True

    def getAllInRange(self, start, end):
        """RETURNS A LIST OF OBJECTS THAT FALL WITHIN THE START AND END DATE RANGE"""
        try:
            remotedb = self.remoteMongo(
                "mongodb://%s:%s" % (self.server, self.port),
                tls=self.tls,
            )
            result = list(remotedb.ELET2415.climo.find("""Add your query here"""))
        except Exception as e:
            msg = str(e)
            print("getAllInRange error", msg)
        else:
            return result

    def humidityMMAR(self, start, end):
        """RETURNS MIN, MAX, AVG AND RANGE FOR HUMIDITY WITHIN THE START AND END DATE RANGE"""
        try:
            remotedb = self.remoteMongo(
                "mongodb://%s:%s" % (self.server, self.port),
                tls=self.tls,
            )
            result = list(
                remotedb.ELET2415.climo.aggregate(
                    """Add your Aggregation pipeline here in this function"""
                )
            )
        except Exception as e:
            msg = str(e)
            print("humidityMMAS error", msg)
        else:
            return result

    def temperatureMMAR(self, start, end):
        """RETURNS MIN, MAX, AVG AND RANGE FOR TEMPERATURE WITHIN THE START AND END DATE RANGE"""
        try:
            remotedb = self.remoteMongo(
                "mongodb://%s:%s" % (self.server, self.port),
                tls=self.tls,
            )
            result = list(
                remotedb.ELET2415.climo.aggregate(
                    """Add your Aggregation pipeline here in this function"""
                )
            )
        except Exception as e:
            msg = str(e)
            print("temperatureMMAS error", msg)
        else:
            return result

    def frequencyDistro(self, variable, start, end):
        """RETURNS FREQUENCY DISTRIBUTION FOR A SPECIFIED VARIABLE WITHIN THE START AND END DATE RANGE"""
        try:
            remotedb = self.remoteMongo(
                "mongodb://%s:%s" % (self.server, self.port),
                tls=self.tls,
            )
            result = list(
                remotedb.ELET2415.climo.aggregate(
                    """Add your Aggregation pipeline here in this function"""
                )
            )
        except Exception as e:
            msg = str(e)
            print("frequencyDistro error", msg)
        else:
            return result


def main():
    from config import Config
    from time import time

    one = DB(Config)

    start = time()
    end = time()
    print(f"completed in: {end - start} seconds")


if __name__ == "__main__":
    main()