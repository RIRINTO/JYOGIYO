/* Drop Tables */

DROP TABLE BUY CASCADE CONSTRAINTS;
DROP TABLE MENU CASCADE CONSTRAINTS;
DROP TABLE CATEGORY CASCADE CONSTRAINTS;
DROP TABLE EVENT CASCADE CONSTRAINTS;
DROP TABLE NOTICE CASCADE CONSTRAINTS;
DROP TABLE SYS_ANSWER CASCADE CONSTRAINTS;
DROP TABLE SYS_QUESTION CASCADE CONSTRAINTS;
DROP TABLE OWNER CASCADE CONSTRAINTS;


/* Create Tables */

CREATE TABLE BUY
(
    -- 주문 번호
    BUY_SEQ    number NOT NULL,
    -- 메뉴 번호
    MENU_SEQ   number NOT NULL,
    -- 수량
    BUY_CNT    number,
    IN_DATE    varchar2(15),
    IN_USER_ID varchar2(20),
    UP_DATE    varchar2(15),
    UP_USER_ID varchar2(20),
    PRIMARY KEY (BUY_SEQ)
);


CREATE TABLE CATEGORY
(
    -- 카테고리 번호
    CATE_SEQ        number NOT NULL,
    -- 회원 번호
    OWNER_SEQ       number NOT NULL,
    -- 카테고리 이름
    CATE_NAME       varchar2(100),
    -- 설명
    CATE_CONTENT    varchar2(3000),
    -- 표시 여부
    CATE_DISPLAY_YN char(1),
    -- 이미지 파일 저장 경로
    ATTACH_PATH     varchar2(100),
    -- 이미지 파일명
    ATTACH_FILE     varchar2(50),
    IN_DATE         varchar2(15),
    IN_USER_ID      varchar2(20),
    UP_DATE         varchar2(15),
    UP_USER_ID      varchar2(20),
    PRIMARY KEY (CATE_SEQ)
);


CREATE TABLE EVENT
(
    -- 이벤트 번호
    EVENT_SEQ     number NOT NULL,
    -- 회원 번호
    OWNER_SEQ     number NOT NULL,
    -- 제목
    EVENT_TITLE   varchar2(150),
    -- 내용
    EVENT_CONTENT varchar2(3000),
    -- 시작일
    EVENT_START   date,
    -- 종료일
    EVENT_END     date,
    -- 파일 저장 경로
    ATTACH_PATH   varchar2(100),
    -- 파일명
    ATTACH_FILE   varchar2(50),
    IN_DATE       varchar2(15),
    IN_USER_ID    varchar2(20),
    UP_DATE       varchar2(15),
    UP_USER_ID    varchar2(20),
    PRIMARY KEY (EVENT_SEQ, OWNER_SEQ)
);


CREATE TABLE MENU
(
    -- 메뉴 번호
    MENU_SEQ        number NOT NULL,
    -- 회원 번호
    OWNER_SEQ       number NOT NULL,
    -- 카테고리 번호
    CATE_SEQ        number NOT NULL,
    -- 이름
    MENU_NAME       varchar2(100),
    -- 가격
    MENU_PRICE      number,
    -- 설명
    MENU_CONTENT    varchar2(3000),
    -- 표시 여부
    MENU_DISPLAY_YN char(1),
    -- 이미지 파일 저장 경로
    ATTACH_PATH     varchar2(100),
    -- 이미지 파일명
    ATTACH_FILE     varchar2(50),
    IN_DATE         varchar2(15),
    IN_USER_ID      varchar2(20),
    UP_DATE         varchar2(15),
    UP_USER_ID      varchar2(20),
    PRIMARY KEY (MENU_SEQ)
);


CREATE TABLE NOTICE
(
    -- 공지 번호
    NOTI_SEQ        number NOT NULL,
    -- 제목
    NOTI_TITLE      varchar2(150),
    -- 내용
    NOTI_CONTENT    varchar2(3000),
    -- 표시 여부
    NOTI_DISPLAY_YN char(1),
    -- 파일 저장 경로
    ATTACH_PATH     varchar2(100),
    -- 파일명
    ATTACH_FILE     varchar2(50),
    IN_DATE         varchar2(15),
    IN_USER_ID      varchar2(20),
    UP_DATE         varchar2(15),
    UP_USER_ID      varchar2(20),
    PRIMARY KEY (NOTI_SEQ)
);


CREATE TABLE OWNER
(
    -- 회원 번호
    OWNER_SEQ      number NOT NULL,
    -- 이름
    OWNER_NAME     varchar2(100),
    -- EMAIL
    OWNER_ID       varchar2(50) UNIQUE,
    -- 비밀번호
    OWNER_PWD      nvarchar2(50),
    -- 상호명
    OWNER_STR_NAME varchar2(100),
    -- 사업자 등록번호 또는 가맹점 번호
    OWNER_STR_NUM  char(10) UNIQUE,
    -- 전화번호
    OWNER_STR_TEL  varchar2(11),
    -- 우편번호
    OWNER_POST     char(5),
    -- 주소1
    OWNER_ADD1     varchar2(150),
    -- 주소2
    OWNER_ADD2     varchar2(150),
    -- 이미지 파일 저장 경로
    LOGO_PATH      varchar2(100),
    -- 이미지 파일명
    LOGO_FILE      varchar2(50),
    ADMIN_YN       char(1) DEFAULT 'N',
    IN_DATE        varchar2(15),
    IN_USER_ID     varchar2(20),
    UP_DATE        varchar2(15),
    UP_USER_ID     varchar2(20),
    PRIMARY KEY (OWNER_SEQ)
);


CREATE TABLE SYS_ANSWER
(
    -- 시스템 질문 번호
    SYS_QUES_SEQ  number NOT NULL,
    -- 답변
    SYS_ANS_REPLY varchar2(3000),
    IN_DATE       varchar2(15),
    IN_USER_ID    varchar2(20),
    UP_DATE       varchar2(15),
    UP_USER_ID    varchar2(20)
);


CREATE TABLE SYS_QUESTION
(
    -- 시스템 질문 번호
    SYS_QUES_SEQ        number NOT NULL,
    -- 회원 번호
    OWNER_SEQ           number NOT NULL,
    -- 제목
    SYS_QUES_TITLE      varchar2(150),
    -- 내용
    SYS_QUES_CONTENT    varchar2(3000),
    -- 표시 여부
    SYS_QUES_DISPLAY_YN char(1),
    -- 파일 저장 경로
    ATTACH_PATH         varchar2(100),
    -- 파일명
    ATTACH_FILE         varchar2(50),
    IN_DATE             varchar2(15),
    IN_USER_ID          varchar2(20),
    UP_DATE             varchar2(15),
    UP_USER_ID          varchar2(20),
    PRIMARY KEY (SYS_QUES_SEQ)
);


/* Create Foreign Keys */

ALTER TABLE MENU
    ADD FOREIGN KEY (CATE_SEQ)
        REFERENCES CATEGORY (CATE_SEQ)
;


ALTER TABLE BUY
    ADD FOREIGN KEY (MENU_SEQ)
        REFERENCES MENU (MENU_SEQ)
;


ALTER TABLE CATEGORY
    ADD FOREIGN KEY (OWNER_SEQ)
        REFERENCES OWNER (OWNER_SEQ)
;


ALTER TABLE EVENT
    ADD FOREIGN KEY (OWNER_SEQ)
        REFERENCES OWNER (OWNER_SEQ)
;


ALTER TABLE MENU
    ADD FOREIGN KEY (OWNER_SEQ)
        REFERENCES OWNER (OWNER_SEQ)
;


ALTER TABLE SYS_QUESTION
    ADD FOREIGN KEY (OWNER_SEQ)
        REFERENCES OWNER (OWNER_SEQ)
;


ALTER TABLE SYS_ANSWER
    ADD FOREIGN KEY (SYS_QUES_SEQ)
        REFERENCES SYS_QUESTION (SYS_QUES_SEQ)
;


/* Comments */

COMMENT
ON COLUMN BUY.BUY_SEQ IS '주문 번호';
COMMENT
ON COLUMN BUY.MENU_SEQ IS '메뉴 번호';
COMMENT
ON COLUMN BUY.BUY_CNT IS '수량';
COMMENT
ON COLUMN CATEGORY.CATE_SEQ IS '카테고리 번호';
COMMENT
ON COLUMN CATEGORY.OWNER_SEQ IS '회원 번호';
COMMENT
ON COLUMN CATEGORY.CATE_NAME IS '카테고리 이름';
COMMENT
ON COLUMN CATEGORY.CATE_CONTENT IS '설명';
COMMENT
ON COLUMN CATEGORY.CATE_DISPLAY_YN IS '표시 여부';
COMMENT
ON COLUMN CATEGORY.ATTACH_PATH IS '이미지 파일 저장 경로';
COMMENT
ON COLUMN CATEGORY.ATTACH_FILE IS '이미지 파일명';
COMMENT
ON COLUMN EVENT.EVENT_SEQ IS '이벤트 번호';
COMMENT
ON COLUMN EVENT.OWNER_SEQ IS '회원 번호';
COMMENT
ON COLUMN EVENT.EVENT_TITLE IS '제목';
COMMENT
ON COLUMN EVENT.EVENT_CONTENT IS '내용';
COMMENT
ON COLUMN EVENT.EVENT_START IS '시작일';
COMMENT
ON COLUMN EVENT.EVENT_END IS '종료일';
COMMENT
ON COLUMN EVENT.ATTACH_PATH IS '파일 저장 경로';
COMMENT
ON COLUMN EVENT.ATTACH_FILE IS '파일명';
COMMENT
ON COLUMN MENU.MENU_SEQ IS '메뉴 번호';
COMMENT
ON COLUMN MENU.OWNER_SEQ IS '회원 번호';
COMMENT
ON COLUMN MENU.CATE_SEQ IS '카테고리 번호';
COMMENT
ON COLUMN MENU.MENU_NAME IS '이름';
COMMENT
ON COLUMN MENU.MENU_PRICE IS '가격';
COMMENT
ON COLUMN MENU.MENU_CONTENT IS '설명';
COMMENT
ON COLUMN MENU.MENU_DISPLAY_YN IS '표시 여부';
COMMENT
ON COLUMN MENU.ATTACH_PATH IS '이미지 파일 저장 경로';
COMMENT
ON COLUMN MENU.ATTACH_FILE IS '이미지 파일명';
COMMENT
ON COLUMN NOTICE.NOTI_SEQ IS '공지 번호';
COMMENT
ON COLUMN NOTICE.NOTI_TITLE IS '제목';
COMMENT
ON COLUMN NOTICE.NOTI_CONTENT IS '내용';
COMMENT
ON COLUMN NOTICE.NOTI_DISPLAY_YN IS '표시 여부';
COMMENT
ON COLUMN NOTICE.ATTACH_PATH IS '파일 저장 경로';
COMMENT
ON COLUMN NOTICE.ATTACH_FILE IS '파일명';
COMMENT
ON COLUMN OWNER.OWNER_SEQ IS '회원 번호';
COMMENT
ON COLUMN OWNER.OWNER_NAME IS '이름';
COMMENT
ON COLUMN OWNER.OWNER_ID IS 'EMAIL';
COMMENT
ON COLUMN OWNER.OWNER_PWD IS '비밀번호';
COMMENT
ON COLUMN OWNER.OWNER_STR_NAME IS '상호명';
COMMENT
ON COLUMN OWNER.OWNER_STR_NUM IS '사업자 등록번호 또는 가맹점 번호';
COMMENT
ON COLUMN OWNER.OWNER_STR_TEL IS '전화번호';
COMMENT
ON COLUMN OWNER.OWNER_POST IS '우편번호';
COMMENT
ON COLUMN OWNER.OWNER_ADD1 IS '주소1';
COMMENT
ON COLUMN OWNER.OWNER_ADD2 IS '주소2';
COMMENT
ON COLUMN OWNER.LOGO_PATH IS '이미지 파일 저장 경로';
COMMENT
ON COLUMN OWNER.LOGO_FILE IS '이미지 파일명';
COMMENT
ON COLUMN SYS_ANSWER.SYS_QUES_SEQ IS '시스템 질문 번호';
COMMENT
ON COLUMN SYS_ANSWER.SYS_ANS_REPLY IS '답변';
COMMENT
ON COLUMN SYS_QUESTION.SYS_QUES_SEQ IS '시스템 질문 번호';
COMMENT
ON COLUMN SYS_QUESTION.OWNER_SEQ IS '회원 번호';
COMMENT
ON COLUMN SYS_QUESTION.SYS_QUES_TITLE IS '제목';
COMMENT
ON COLUMN SYS_QUESTION.SYS_QUES_CONTENT IS '내용';
COMMENT
ON COLUMN SYS_QUESTION.SYS_QUES_DISPLAY_YN IS '표시 여부';
COMMENT
ON COLUMN SYS_QUESTION.ATTACH_PATH IS '파일 저장 경로';
COMMENT
ON COLUMN SYS_QUESTION.ATTACH_FILE IS '파일명';



