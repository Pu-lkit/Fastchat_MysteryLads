--
-- PostgreSQL database dump
--

-- Dumped from database version 12.12 (Ubuntu 12.12-0ubuntu0.20.04.1)
-- Dumped by pg_dump version 12.12 (Ubuntu 12.12-0ubuntu0.20.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: groups; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.groups (
    groupname text NOT NULL,
    publickey text
);


ALTER TABLE public.groups OWNER TO postgres;

--
-- Name: groupusershash; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.groupusershash (
    username text NOT NULL,
    isadmin integer
);


ALTER TABLE public.groupusershash OWNER TO postgres;

--
-- Name: tablea; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tablea (
    otherusername text,
    message text
);


ALTER TABLE public.tablea OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    username text NOT NULL,
    password text,
    isonline integer,
    publickey text
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: groups groups_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.groups
    ADD CONSTRAINT groups_pkey PRIMARY KEY (groupname);


--
-- Name: groupusershash groupusershash_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.groupusershash
    ADD CONSTRAINT groupusershash_pkey PRIMARY KEY (username);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (username);


--
-- PostgreSQL database dump complete
--


