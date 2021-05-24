from config import *
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Sequence, UniqueConstraint
import csv

engine = create_engine('sqlite:///'+SQLITE_DB_NAME, echo = True)
meta = MetaData()

has_header=True
contacts = Table(
      'contacts', meta,
      Column('id',Integer,Sequence('Contact_seq_id'),primary_key = True),
      Column('first', String), 
      Column('last', String),
      Column('isdnnumber',String),
      Column('isdnnumbertwo',String),
      Column('isdnbandwidth',String),
      Column('restricted',String),
      Column('phone',String),
      Column('email',String),
      Column('h23',String),
      Column('ipaddress',String),
      Column('ipbandwidth',String),
      Column('externalid',String),
      UniqueConstraint('first', 'email', name='first_email_uniq')
   )

def create_tables():
   meta.create_all(engine)

def populate_from_file(filename,has_header = True):
    conn = engine.connect()
    print('Reading from file {}'.format(filename))
    with open(filename, newline ='') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        for record in reader:
            if reader.line_num==1 and has_header:
                continue
            else:
                name=record[0].strip().rsplit(maxsplit=1)
                ins=contacts.insert().values(
                    first=name[0],
                    last=name[1],
                    isdnnumber=record[1],
                    isdnnumbertwo=record[2],
                    isdnbandwidth=record[3],
                    restricted=record[4],
                    phone=record[5].strip('[]'),
                    email=record[6],
                    h23=record[7],
                    ipaddress=record[8],
                    ipbandwidth=record[9],
                    externalid=record[10])
                try:
                    conn.execute(ins)
                except Exception as error:
                    print(error)
                    continue

if __name__ == '__main__':
   filename='PhonebookExportFile.txt'
   create_tables()
   populate_from_file(filename)

