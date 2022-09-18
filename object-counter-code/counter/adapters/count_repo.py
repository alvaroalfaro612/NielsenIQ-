from typing import List

from pymongo import MongoClient
import psycopg2

from counter.domain.models import ObjectCount
from counter.domain.ports import ObjectCountRepo


class CountInMemoryRepo(ObjectCountRepo):

    def __init__(self):
        self.store = dict()

    def read_values(self, object_classes: List[str] = None) -> List[ObjectCount]:
        if object_classes is None:
            return list(self.store.values())

        return [self.store.get(object_class) for object_class in object_classes]

    def update_values(self, new_values: List[ObjectCount]):
        for new_object_count in new_values:
            key = new_object_count.object_class
            try:
                stored_object_count = self.store[key]
                self.store[key] = ObjectCount(key, stored_object_count.count + new_object_count.count)
            except KeyError:
                self.store[key] = ObjectCount(key, new_object_count.count)


class CountMongoDBRepo(ObjectCountRepo):

    def __init__(self, host, port, database):
        self.__host = host
        self.__port = port
        self.__database = database

    def __get_counter_col(self):
        client = MongoClient(self.__host, self.__port)
        db = client[self.__database]
        counter_col = db.counter
        return counter_col

    def read_values(self, object_classes: List[str] = None) -> List[ObjectCount]:
        counter_col = self.__get_counter_col()
        query = {"object_class": {"$in": object_classes}} if object_classes else None
        counters = counter_col.find(query)
        object_counts = []
        for counter in counters:
            object_counts.append(ObjectCount(counter['object_class'], counter['count']))
        return object_counts

    def update_values(self, new_values: List[ObjectCount]):
        counter_col = self.__get_counter_col()
        for value in new_values:
            counter_col.update_one({'object_class': value.object_class}, {'$inc': {'count': value.count}}, upsert=True)

class CountPostgreRepo(ObjectCountRepo): #class implementing ObjectCountRepo using postgresql

    def __init__(self, host, port, database, password, user): 
        self.__host = host
        self.__port = port
        self.__database = database
        self.__password= password
        self.__user= user

    def __get_connection(self): #returns the connection to the db
        conn=psycopg2.connect(host=self.__host, database=self.__database, user=self.__user, port=self.__port, password=self.__password)
        return conn

    def read_values(self, object_classes: List[str] = None) -> List[ObjectCount]: #returns the number of each class stored in the postgresql
        conn=self.__get_connection()
        cur=conn.cursor()
        cur.execute('SELECT class_name, counts FROM counts')
        counters=cur.fetchall()
        cur.close()
        conn.close()
        # TODO: use enums instead of numbers (index 0 for object class and index 1 for count value)
        return [ObjectCount(counter[0], counter[1]) for counter in counters ]

    def update_values(self, new_values: List[ObjectCount]): #update the counter for each class in the postgresql fb
        conn=self.__get_connection()
        cur=conn.cursor()
        for value in new_values:
            cur.execute('SELECT class_name, counts FROM counts WHERE class_name= %s',(value.object_class,))
            if cur.fetchone() is not None: #if there is already a row with this class count -> update
                cur.execute('UPDATE counts SET counts=counts + %s WHERE class_name= %s',(str(value.count), value.object_class,))
            else: #if it is the first time appearing this class -> insert
                cur.execute('INSERT INTO counts (class_name,counts) VALUES(%s, %s)',(value.object_class, str(value.count),))
        conn.commit()
        cur.close()
        conn.close()