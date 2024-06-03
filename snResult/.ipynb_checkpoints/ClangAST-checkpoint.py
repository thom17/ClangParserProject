from sqlalchemy import create_engine, Column, Integer, Float, String, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()

class TClangAST(Base):
    __tablename__ = 'ClangAST'
    srcSig: str = Column(String, primary_key=True)
    astStr = Column(String)
    sourceCode = Column(String)
    # 관계 설정

    def get_class_name(self):
        return self.srcSig.split('.')[0]


if __name__ == "__main__":
    # 데이터베이스 엔진 생성 (예: SQLite 메모리 데이터베이스)
    engine = create_engine('sqlite:///dataset.db')
    Base.metadata.create_all(engine)

    # 세션 생성
    Session = sessionmaker(bind=engine)
    session = Session()

    # 검색 쿼리
    # 모든 실행
    asts = session.query(TClangAST).all()
    for ast in asts:
        print(ast.srcSig, " : ", ast.get_class_name())
        # print(ast.srcSig, ast.astStr)


def get_all_table(path: str = 'dataset.db') -> [TClangAST]:
    engine = create_engine('sqlite:///'+path)
    Base.metadata.create_all(engine)

    # 세션 생성
    Session = sessionmaker(bind=engine)
    session = Session()

    # 검색 쿼리
    # 모든 실행
    return session.query(TClangAST).all()