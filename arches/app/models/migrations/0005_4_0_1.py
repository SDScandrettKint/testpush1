# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2017-04-25 11:36
from __future__ import unicode_literals

import os
from django.db import migrations, models
from django.core import management
from arches.app.models.system_settings import settings
from arches.app.models.concept import Concept
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.elasticsearch_dsl_builder import Term, Query
from rdflib import Graph, RDF, RDFS

def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    extensions = [os.path.join(settings.ONTOLOGY_PATH, x) for x in settings.ONTOLOGY_EXT]
    management.call_command('load_ontology', source=os.path.join(settings.ONTOLOGY_PATH, settings.ONTOLOGY_BASE),
        version=settings.ONTOLOGY_BASE_VERSION, ontology_name=settings.ONTOLOGY_BASE_NAME, id='e6e8db47-2ccf-11e6-927e-b8f6b115d7dd', extensions=','.join(extensions), verbosity=0)

    Ontology = apps.get_model("models", "Ontology")
    Node = apps.get_model("models", "Node")
    Edge = apps.get_model("models", "Edge")

    for ontology in Ontology.objects.filter(parentontology=None):
        g = Graph()
        g.parse(ontology.path.path)
        for extension in Ontology.objects.filter(parentontology=ontology):
            g.parse(extension.path.path)

        ontology_classes = set()
        ontology_properties = set()
        for ontology_property,p,o in g.triples((None, None, RDF.Property)):
            ontology_properties.add(ontology_property)
            for s,p,domain_class in g.triples((ontology_property, RDFS.domain, None)):
                ontology_classes.add(domain_class)
            for s,p,range_class in g.triples((ontology_property, RDFS.range, None)):
                ontology_classes.add(range_class)

        for ontology_class,p,o in g.triples((None, None, RDFS.Class)):
            ontology_classes.add(ontology_class)

        for ontology_class in ontology_classes:
            for node in Node.objects.filter(ontologyclass=str(ontology_class).split('/')[-1], graph__in=ontology.graphs.all()):
                node.ontologyclass = ontology_class
                node.save()

        for ontology_property in ontology_properties:
            for edge in Edge.objects.filter(ontologyproperty=str(ontology_property).split('/')[-1], graph__in=ontology.graphs.all()):
                edge.ontologyproperty = ontology_property
                edge.save()

    # index base Arches concept
    arches_concept = Concept().get(id='00000000-0000-0000-0000-000000000001', include=['label'])
    arches_concept.index()

    DValueType = apps.get_model("models", "DValueType")
    DValueType.objects.create(valuetype='identifier', category='identifiers', namespace='dcterms', datatype='text')

def reverse_func(apps, schema_editor):
    extensions = [os.path.join(settings.ONTOLOGY_PATH, x) for x in settings.ONTOLOGY_EXT]
    management.call_command('load_ontology', source=os.path.join(settings.ONTOLOGY_PATH, settings.ONTOLOGY_BASE),
        version=settings.ONTOLOGY_BASE_VERSION, ontology_name=settings.ONTOLOGY_BASE_NAME, id='e6e8db47-2ccf-11e6-927e-b8f6b115d7dd', extensions=','.join(extensions), verbosity=0)

    Node = apps.get_model("models", "Node")
    Edge = apps.get_model("models", "Edge")

    for node in Node.objects.all():
        node.ontologyclass = str(node.ontologyclass).split('/')[-1]
        node.save()

    for edge in Edge.objects.all():
        edge.ontologyproperty = str(edge.ontologyproperty).split('/')[-1]
        edge.save()

    # remove index for base Arches concept
    se = SearchEngineFactory().create()
    query = Query(se, start=0, limit=10000)
    query.add_query(Term(field='conceptid', term='00000000-0000-0000-0000-000000000001'))
    query.delete(index='concepts')

    try:
        DValueType = apps.get_model("models", "DValueType")
        DValueType.objects.get(valuetype='identifier').delete()
    except:
        pass

class Migration(migrations.Migration):

    dependencies = [
        ('models', '0004_4_0_1'),
    ]

    operations = [
        migrations.RunSQL("""
            INSERT INTO widgets(
                widgetid,
                name,
                component,
                datatype,
                defaultconfig
            ) VALUES (
                '31f3728c-7613-11e7-a139-784f435179ea',
                'resource-instance-select-widget',
                'views/components/widgets/resource-instance-select',
                'resource-instance',
                '{
                    "placeholder": ""
                }'
            );

            INSERT INTO d_data_types(
                datatype, iconclass, modulename,
                classname, defaultconfig, configcomponent,
                configname, isgeometric, defaultwidget,
                issearchable
            ) VALUES (
                'resource-instance',
                'fa fa-external-link-o',
                'datatypes.py',
                'ResourceInstanceDataType',
                '{
                    "graphid": null
                }',
                'views/components/datatypes/resource-instance',
                'resource-instance-datatype-config',
                FALSE,
                '31f3728c-7613-11e7-a139-784f435179ea',
                TRUE
            );

            INSERT INTO widgets(
                widgetid,
                name,
                component,
                datatype,
                defaultconfig
            ) VALUES (
                'ff3c400a-76ec-11e7-a793-784f435179ea',
                'resource-instance-multiselect-widget',
                'views/components/widgets/resource-instance-multiselect',
                'resource-instance-list',
                '{
                    "placeholder": ""
                }'
            );

            INSERT INTO d_data_types(
                datatype, iconclass, modulename,
                classname, defaultconfig, configcomponent,
                configname, isgeometric, defaultwidget,
                issearchable
            ) VALUES (
                'resource-instance-list',
                'fa fa-external-link-square',
                'datatypes.py',
                'ResourceInstanceDataType',
                '{
                    "graphid": null
                }',
                'views/components/datatypes/resource-instance',
                'resource-instance-datatype-config',
                FALSE,
                'ff3c400a-76ec-11e7-a793-784f435179ea',
                TRUE
            );
            """,
            """
            DELETE FROM d_data_types
                WHERE datatype = 'resource-instance';

            DELETE from widgets
                WHERE widgetid = '31f3728c-7613-11e7-a139-784f435179ea';

            DELETE FROM d_data_types
                WHERE datatype = 'resource-instance-list';

            DELETE from widgets
                WHERE widgetid = 'ff3c400a-76ec-11e7-a793-784f435179ea';
        """),
        migrations.RunSQL("""
            UPDATE public.nodes
               SET ontologyclass='E93_Presence'
             WHERE ontologyclass='E94_Space';

            UPDATE public.edges
               SET ontologyproperty='P167i_was_place_of'
             WHERE ontologyproperty='P167i_was_place_at';

            UPDATE public.edges
               SET ontologyproperty='P167i_was_place_of'
             WHERE ontologyproperty='P168_place_is_defined_by';

            UPDATE public.edges
               SET ontologyproperty='P167_was_at'
             WHERE ontologyproperty='P168i_defines_place';
            """,
            """
            UPDATE public.nodes
               SET ontologyclass='E94_Space'
             WHERE ontologyclass='E93_Presence';

            UPDATE public.edges
               SET ontologyproperty='P168_place_is_defined_by'
             WHERE ontologyproperty='P167i_was_place_of';

            UPDATE public.edges
               SET ontologyproperty='P168i_defines_place'
             WHERE ontologyproperty='P167_was_at';

            UPDATE public.edges
               SET ontologyproperty='P167i_was_place_at'
             WHERE ontologyproperty='P167i_was_place_of';
        """),
        migrations.RunPython(forwards_func, reverse_func),
    ]
