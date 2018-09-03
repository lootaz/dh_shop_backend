from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Shop, Schedule, TimeRange


class TimeRangeSerializer(serializers.ModelSerializer):
    from_t = serializers.TimeField(format='%H:%M')
    to_t = serializers.TimeField(format='%H:%M')
    schedule = serializers.PrimaryKeyRelatedField(queryset=Schedule.objects.all(),
                                                  required=False,
                                                  write_only=True)

    class Meta:
        model = TimeRange
        fields = ('id', 'from_t', 'to_t', 'is_open', 'reason', 'schedule')
        extra_kwargs = {
            'id': {'read_only': True}
        }


class ScheduleSerializer(serializers.ModelSerializer):
    time_ranges = TimeRangeSerializer(many=True, required=True)
    shop = serializers.PrimaryKeyRelatedField(queryset=Shop.objects.all(),
                                              required=False,
                                              write_only=True)

    class Meta:
        model = Schedule
        fields = ('id', 'day_of_week', 'shop', 'time_ranges')
        extra_kwargs = {
            'id': {'read_only': True}
        }

    def create(self, validated_data):
        time_ranges_data = validated_data.pop('time_ranges')
        schedule = Schedule.objects.create(**validated_data)
        for time_range_data in time_ranges_data:
            time_range_data['schedule'] = schedule
            TimeRangeSerializer.create(TimeRangeSerializer(), time_range_data)
        return schedule


class ShopListSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Shop
        fields = ('id', 'owner', 'title')
        read_only_fields = fields


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password')
        extra_kwargs = {
            'id': {'read_only': True},
            'password': {'write_only': True}
        }


class ShopSerializer(serializers.ModelSerializer):
    schedules = ScheduleSerializer(many=True, required=True)
    owner = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),
                                               required=False,
                                               write_only=True)
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)

    class Meta:
        model = Shop
        fields = ('id', 'owner', 'owner_id', 'title', 'schedules')

    def create(self, validated_data):
        schedules_data = validated_data.pop('schedules')
        shop = Shop.objects.create(**validated_data)

        for schedule_data in schedules_data:
            schedule_data['shop'] = shop
            ScheduleSerializer.create(ScheduleSerializer(), validated_data=schedule_data)

        return shop
