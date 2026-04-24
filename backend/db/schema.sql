--
-- PostgreSQL database dump
--

-- Dumped from database version 17.4
-- Dumped by pg_dump version 17.5 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA public;


--
-- Name: user_provided_occasion; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.user_provided_occasion AS ENUM (
    'wedding',
    'birthday',
    'anniversary',
    'other'
);


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: assets; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.assets (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    asset_key_original text NOT NULL,
    asset_key_display text,
    asset_key_llm text,
    metadata_json jsonb,
    created_at timestamp without time zone DEFAULT now(),
    original_photobook_id uuid
);


--
-- Name: jobs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.jobs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    job_type text NOT NULL,
    status text DEFAULT 'queued'::text NOT NULL,
    input_payload jsonb,
    result_payload jsonb,
    error_message text,
    user_id uuid,
    photobook_id uuid,
    created_at timestamp without time zone DEFAULT now(),
    started_at timestamp without time zone,
    completed_at timestamp without time zone
);


--
-- Name: pages; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.pages (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    photobook_id uuid,
    page_number integer NOT NULL,
    user_message text,
    layout text,
    created_at timestamp without time zone DEFAULT now()
);


--
-- Name: pages_assets_rel; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.pages_assets_rel (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    page_id uuid,
    asset_id uuid,
    order_index integer,
    caption text
);


--
-- Name: photobooks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.photobooks (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    title text NOT NULL,
    caption text,
    theme text,
    status text DEFAULT 'draft'::text,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    user_provided_occasion public.user_provided_occasion,
    user_provided_occasion_custom_details text
);


--
-- Name: schema_migrations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.schema_migrations (
    version character varying NOT NULL
);


--
-- Data for Name: assets; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.assets (id, user_id, asset_key_original, asset_key_display, asset_key_llm, metadata_json, created_at, original_photobook_id) FROM stdin;
43c5fbf6-ff4f-4d88-8e8d-e528bd79de72	ab9cba02-b210-4f73-9f87-548bf28e4367	uploads/job_3ef61cffe0e64576a34721dbd31c982b/b98b53088ede4793b1139226bdee4e42.png	<FIXME>	<FIXME>	{}	2025-07-03 16:19:47.109165	\N
b1d4e267-7c00-4edf-9e61-d2cc7d8e7bc7	ab9cba02-b210-4f73-9f87-548bf28e4367	uploads/job_3ef61cffe0e64576a34721dbd31c982b/ca02ad0b49ff449598b936329987f9ed.png	<FIXME>	<FIXME>	{}	2025-07-03 16:19:47.109382	\N
4562a0b2-8f64-4cea-b92a-6027317fa805	ab9cba02-b210-4f73-9f87-548bf28e4367	uploads/job_3ef61cffe0e64576a34721dbd31c982b/cbb78ee8972a45fda775e0378976b575.png	<FIXME>	<FIXME>	{}	2025-07-03 16:19:47.109454	\N
564bd208-b340-4927-98b6-9f797981933f	ab9cba02-b210-4f73-9f87-548bf28e4367	uploads/job_3ef61cffe0e64576a34721dbd31c982b/f0f89f5b3c124760a1eeed80e626f86d.png	<FIXME>	<FIXME>	{}	2025-07-03 16:19:47.109517	\N
5c14e152-89a3-4bf8-8402-1758740d6348	ab9cba02-b210-4f73-9f87-548bf28e4367	uploads/job_3ef61cffe0e64576a34721dbd31c982b/d858a2dc4a80478995fe8bd7980f6887.png	<FIXME>	<FIXME>	{}	2025-07-03 16:19:47.109577	\N
16f5bc14-1c9b-40f1-b8cc-05e0becdf7a5	ab9cba02-b210-4f73-9f87-548bf28e4367	uploads/job_3ef61cffe0e64576a34721dbd31c982b/9254f760d06f458094e5a6abdd079ed2.png	<FIXME>	<FIXME>	{}	2025-07-03 16:19:47.109631	\N
\.


--
-- Data for Name: jobs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.jobs (id, job_type, status, input_payload, result_payload, error_message, user_id, photobook_id, created_at, started_at, completed_at) FROM stdin;
\.


--
-- Data for Name: pages; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.pages (id, photobook_id, page_number, user_message, layout, created_at) FROM stdin;
\.


--
-- Data for Name: pages_assets_rel; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.pages_assets_rel (id, page_id, asset_id, order_index, caption) FROM stdin;
\.


--
-- Data for Name: photobooks; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.photobooks (id, user_id, title, caption, theme, status, created_at, updated_at, user_provided_occasion, user_provided_occasion_custom_details) FROM stdin;
ae9f6ab2-de34-4b00-a1c7-6a2d6e20323b	e352597b-ee4c-4eff-b977-707190e3e256	New Photobook 2025-07-03 08:39	\N	\N	pending	2025-07-03 15:39:12.704887	2025-07-03 15:39:12.704893	\N	\N
5a73a161-6801-49df-b864-bc42e0592fd8	ab9cba02-b210-4f73-9f87-548bf28e4367	New Photobook 2025-07-03 09:19	\N	\N	pending	2025-07-03 16:19:46.687604	2025-07-03 16:19:46.687606	\N	\N
\.


--
-- Data for Name: schema_migrations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.schema_migrations (version) FROM stdin;
20250703021505
20250703025351
20250703160659
20250703174524
\.


--
-- Name: assets assets_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.assets
    ADD CONSTRAINT assets_pkey PRIMARY KEY (id);


--
-- Name: jobs jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_pkey PRIMARY KEY (id);


--
-- Name: pages_assets_rel pages_assets_rel_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pages_assets_rel
    ADD CONSTRAINT pages_assets_rel_pkey PRIMARY KEY (id);


--
-- Name: pages pages_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pages
    ADD CONSTRAINT pages_pkey PRIMARY KEY (id);


--
-- Name: photobooks photobooks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.photobooks
    ADD CONSTRAINT photobooks_pkey PRIMARY KEY (id);


--
-- Name: schema_migrations schema_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schema_migrations
    ADD CONSTRAINT schema_migrations_pkey PRIMARY KEY (version);


--
-- Name: assets assets_original_photobook_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.assets
    ADD CONSTRAINT assets_original_photobook_id_fkey FOREIGN KEY (original_photobook_id) REFERENCES public.photobooks(id);


--
-- Name: jobs jobs_photobook_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_photobook_id_fkey FOREIGN KEY (photobook_id) REFERENCES public.photobooks(id);


--
-- Name: pages_assets_rel pages_assets_rel_asset_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pages_assets_rel
    ADD CONSTRAINT pages_assets_rel_asset_id_fkey FOREIGN KEY (asset_id) REFERENCES public.assets(id);


--
-- Name: pages_assets_rel pages_assets_rel_page_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pages_assets_rel
    ADD CONSTRAINT pages_assets_rel_page_id_fkey FOREIGN KEY (page_id) REFERENCES public.pages(id);


--
-- Name: pages pages_photobook_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pages
    ADD CONSTRAINT pages_photobook_id_fkey FOREIGN KEY (photobook_id) REFERENCES public.photobooks(id);


--
-- PostgreSQL database dump complete
--

