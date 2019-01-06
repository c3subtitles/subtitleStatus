import factory
from factory.django import DjangoModelFactory


from .. import models


class EventFactory(DjangoModelFactory):
    class Meta:
        model = models.Event

    acronym = factory.Sequence('3{0}C3'.format)
    title = factory.Sequence('3{}th Chaos Communication Congress'.format)
    days = 4
    city = 'Hamburg'
    building = 'CCH'

    @factory.lazy_attribute
    def hashtag(self):
        return '#{}'.format(self.acronym)

    @factory.post_generation
    def _add_days(self, create, extraced, **kwargs):
        self._days = [EventDaysFactory(__sequence=day, event=self)
                      for day in range(1, self.days + 1)]


class EventDaysFactory(DjangoModelFactory):
    class Meta:
        model = models.Event_Days

    event = factory.SubFactory(EventFactory)
    index = factory.Sequence(int)
    date = factory.Faker('date_this_decade', before_today=True, after_today=True)


class TrackFactory(DjangoModelFactory):
    class Meta:
        model = models.Tracks

    track = factory.Faker('catch_phrase')


class TypeOfFactory(DjangoModelFactory):
    class Meta:
        model = models.Type_of

    type = factory.Sequence('Type {}'.format)


class StateFactory(DjangoModelFactory):
    class Meta:
        model = models.States

    id = factory.Sequence(int)
    state_en = factory.Sequence('State {}'.format)
    state_de = factory.LazyAttribute(lambda o: o.state_en)


class RoomFactory(DjangoModelFactory):
    class Meta:
        model = models.Rooms

    room = factory.Faker('name')
    building = factory.Faker('company')
