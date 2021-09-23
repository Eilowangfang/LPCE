# contrib/aqo/Makefile

EXTENSION = lpce
EXTVERSION = 1.2
PGFILEDESC = "AQO - Adaptive Query Optimization"
MODULE_big = lpce
OBJS = lpce.o cardinality_estimation.o cardinality_hooks.o \
hash.o  path_utils.o postprocessing.o preprocessing.o \
selectivity_cache.o storage.o utils.o ignorance.o table_utils.o $(WIN32RES)

TAP_TESTS = 1

REGRESS =	aqo_disabled \
			aqo_controlled \
			aqo_intelligent \
			aqo_forced \
			aqo_learn \
			schema \
			aqo_fdw \
			aqo_CVE-2020-14350 \
			gucs \
			forced_stat_collection \
			unsupported

fdw_srcdir = $(top_srcdir)/contrib/postgres_fdw
PG_CPPFLAGS += -lstdc++ -I$(libpq_srcdir) -I$(fdw_srcdir) -I/usr/include/python3.7m -I/usr/lib/python3.7/config-3.7m-x86_64-linux-gnu -L/home/hive/.local/lib/python3.7/site-packages/ -L/usr/lib/python3.7 -lpython3.7m -L/usr/lib -ltest
EXTRA_REGRESS_OPTS=--temp-config=$(top_srcdir)/$(subdir)/conf.add
EXTRA_INSTALL = contrib/postgres_fdw

DATA = aqo--1.0.sql aqo--1.0--1.1.sql aqo--1.1--1.2.sql aqo--1.2.sql

ifdef USE_PGXS
PG_CONFIG ?= pg_config
PGXS := $(shell $(PG_CONFIG) --pgxs)
include $(PGXS)
else
subdir = contrib/LPCE
top_builddir = ../..
include $(top_builddir)/src/Makefile.global
include $(top_srcdir)/contrib/contrib-global.mk
endif

