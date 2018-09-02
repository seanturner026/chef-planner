-- Table: public.dishes

-- DROP TABLE public.dishes;

CREATE TABLE public.dishes
(
    id integer NOT NULL DEFAULT nextval('dishes_id_seq'::regclass),
    dish text COLLATE pg_catalog."default",
    total_duration integer,
    duration integer[],
    instructions text[] COLLATE pg_catalog."default",
    description text COLLATE pg_catalog."default",
    servings integer,
    ingredients text[] COLLATE pg_catalog."default",
    CONSTRAINT dishes_pkey PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.dishes
    OWNER to sean;