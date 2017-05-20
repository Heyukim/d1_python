# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-20 18:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BlockedMemberNode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.CharField(max_length=128, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='EventLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Event')),
            ],
        ),
        migrations.CreateModel(
            name='IdNamespace',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('did', models.CharField(max_length=800, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='IpAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.CharField(max_length=32, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='LocalReplica',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('urn', models.CharField(max_length=64, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.PositiveSmallIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='PreferredMemberNode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('node', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Node')),
            ],
        ),
        migrations.CreateModel(
            name='RemoteReplica',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='ReplicaInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(db_index=True, null=True)),
                ('member_node', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Node')),
            ],
        ),
        migrations.CreateModel(
            name='ReplicaObsolescenceChainReference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pid', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='app.IdNamespace')),
            ],
        ),
        migrations.CreateModel(
            name='ReplicaStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=16, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='ReplicationPolicy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('replication_is_allowed', models.BooleanField(db_index=True)),
                ('desired_number_of_replicas', models.PositiveSmallIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='ReplicationQueue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size', models.BigIntegerField(db_index=True)),
                ('failed_attempts', models.PositiveSmallIntegerField()),
                ('local_replica', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='app.LocalReplica')),
            ],
        ),
        migrations.CreateModel(
            name='ScienceObject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serial_version', models.PositiveIntegerField()),
                ('modified_timestamp', models.DateTimeField(db_index=True)),
                ('uploaded_timestamp', models.DateTimeField(db_index=True)),
                ('checksum', models.CharField(db_index=True, max_length=128)),
                ('size', models.BigIntegerField(db_index=True)),
                ('is_archived', models.BooleanField(db_index=True)),
                ('url', models.CharField(max_length=1024, unique=True)),
                ('authoritative_member_node', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scienceobject_authoritative_member_node', to='app.Node')),
            ],
        ),
        migrations.CreateModel(
            name='ScienceObjectChecksumAlgorithm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('checksum_algorithm', models.CharField(max_length=32, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='ScienceObjectFormat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('format', models.CharField(max_length=128, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='SeriesIdToScienceObject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sciobj', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='app.ScienceObject')),
                ('sid', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='app.IdNamespace')),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=1024, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='SystemMetadataRefreshQueue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serial_version', models.PositiveIntegerField()),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('sysmeta_timestamp', models.DateTimeField()),
                ('failed_attempts', models.PositiveSmallIntegerField()),
                ('sciobj', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='app.ScienceObject')),
            ],
        ),
        migrations.CreateModel(
            name='SystemMetadataRefreshQueueStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=1024, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserAgent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_agent', models.CharField(max_length=1024, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='WhitelistForCreateUpdateDelete',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='app.Subject')),
            ],
        ),
        migrations.AddField(
            model_name='systemmetadatarefreshqueue',
            name='status',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.SystemMetadataRefreshQueueStatus'),
        ),
        migrations.AddField(
            model_name='scienceobject',
            name='checksum_algorithm',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.ScienceObjectChecksumAlgorithm'),
        ),
        migrations.AddField(
            model_name='scienceobject',
            name='format',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.ScienceObjectFormat'),
        ),
        migrations.AddField(
            model_name='scienceobject',
            name='obsoleted_by',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='scienceobject_obsoleted_by', to='app.IdNamespace'),
        ),
        migrations.AddField(
            model_name='scienceobject',
            name='obsoletes',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='scienceobject_obsoletes', to='app.IdNamespace'),
        ),
        migrations.AddField(
            model_name='scienceobject',
            name='origin_member_node',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scienceobject_origin_member_node', to='app.Node'),
        ),
        migrations.AddField(
            model_name='scienceobject',
            name='pid',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='app.IdNamespace'),
        ),
        migrations.AddField(
            model_name='scienceobject',
            name='rights_holder',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scienceobject_rights_holder', to='app.Subject'),
        ),
        migrations.AddField(
            model_name='scienceobject',
            name='submitter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scienceobject_submitter', to='app.Subject'),
        ),
        migrations.AddField(
            model_name='replicationpolicy',
            name='sciobj',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='app.ScienceObject'),
        ),
        migrations.AddField(
            model_name='replicainfo',
            name='status',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.ReplicaStatus'),
        ),
        migrations.AddField(
            model_name='remotereplica',
            name='info',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='app.ReplicaInfo'),
        ),
        migrations.AddField(
            model_name='remotereplica',
            name='sciobj',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.ScienceObject'),
        ),
        migrations.AddField(
            model_name='preferredmembernode',
            name='replication_policy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.ReplicationPolicy'),
        ),
        migrations.AddField(
            model_name='permission',
            name='sciobj',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.ScienceObject'),
        ),
        migrations.AddField(
            model_name='permission',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Subject'),
        ),
        migrations.AddField(
            model_name='localreplica',
            name='info',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='app.ReplicaInfo'),
        ),
        migrations.AddField(
            model_name='localreplica',
            name='pid',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='app.IdNamespace'),
        ),
        migrations.AddField(
            model_name='eventlog',
            name='ip_address',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.IpAddress'),
        ),
        migrations.AddField(
            model_name='eventlog',
            name='sciobj',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.ScienceObject'),
        ),
        migrations.AddField(
            model_name='eventlog',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Subject'),
        ),
        migrations.AddField(
            model_name='eventlog',
            name='user_agent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.UserAgent'),
        ),
        migrations.AddField(
            model_name='blockedmembernode',
            name='node',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Node'),
        ),
        migrations.AddField(
            model_name='blockedmembernode',
            name='replication_policy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.ReplicationPolicy'),
        ),
    ]
