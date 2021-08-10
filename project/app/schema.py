import graphene
from graphene_django import DjangoObjectType
from users.schema import UserType

from .models import Link

class LinkType(DjangoObjectType):
    class Meta:
        model = Link


class Query(graphene.ObjectType):
    links = graphene.List(LinkType)
    my_links = graphene.List(LinkType)

    def resolve_my_links(self, info):
        # queries only the links they own
        if not info.context.user.is_authenticated:
            return Link.objects.none()
        else:
            return Link.objects.filter(owner=info.context.user)

    def resolve_links(self, info, **kwargs):
        return Link.objects.all()

class CreateLink(graphene.Mutation):
    id = graphene.ID()
    url = graphene.String()
    description = graphene.String()
    owner = graphene.Field(UserType)

    class Arguments:
        url = graphene.String()
        description = graphene.String()

    def mutate(self, info, url, description):
        user = info.context.user or None
        if user.is_authenticated:
            link = Link(url=url, description=description, owner=user)
            link.save()
            return CreateLink(
                    id=link.id,
                    url=link.url,
                    description=link.description,
                    owner=link.owner,
            )
        raise Exception('Please Log In')

class UpdateLink(graphene.Mutation):
    id = graphene.ID()
    url = graphene.String()
    description = graphene.String()

    class Arguments:
        id = graphene.ID()
        url = graphene.String()
        description = graphene.String()

    def mutate(self, info, url, description, id):
        user = info.context.user or None
        link = Link(id=id, url=url, description=description)
        link.save()

        return UpdateLink(
            id=link.id,
            url=link.url,
            description=link.description,

        )
class DeleteLink(graphene.Mutation):
    id = graphene.Int()

    class Arguments:
        id = graphene.Int()

    def mutate(self, info, id):
        link = Link(id=id)
        link.delete()

        return DeleteLink(
            id=link.id      
        )

class Mutation(graphene.ObjectType):
    create_link = CreateLink.Field()
    update_link = UpdateLink.Field()
    delete_link = DeleteLink.Field() 