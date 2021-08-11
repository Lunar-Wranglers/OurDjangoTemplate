from django.contrib import auth
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
    owner = graphene.Field(UserType)


    class Arguments:
        id = graphene.ID()
        url = graphene.String()
        description = graphene.String()
        
    def mutate(self, info, url, description, id):
        # get the user object from the request (info.context)
        user = info.context.user
        # This provides a query set of the values of all of the users owned links
        owner_links = Link.objects.filter(owner=info.context.user).values()
        # print(owner_links)
        # iterate through the links
        for owner in owner_links:
            # first we extract the owner as a list
            owner = list(owner.values())
            # the owner is the last value in the list
            owned_id = (owner[0])

            # print([owned_id, int(id)])
            # create a list to store the values of the id in the list of owned ids and the id passed in
            is_owner = (owned_id, int(id))
            # compare the id of the owned links to the id passed in and if the user is logged in
            if is_owner[0] == is_owner[1] and user.is_authenticated:
                # print('authorized')
                # mutate the link based on the arguments below
                link = Link(id=id, url=url, description=description, owner=user)
                # save the link
                link.save()
                # then return it
                return UpdateLink(
                    id=link.id,
                    url=link.url,
                    description=link.description,
                    owner=link.owner
                )
        raise Exception('Not authorized to update this link. Please sign in or try a different link.')
class DeleteLink(graphene.Mutation):
    id = graphene.Int()

    class Arguments:
        id = graphene.Int()

    def mutate(self, info, id):
        user = info.context.user
        # This provides a query set of all of the users owned links
        owner_links = Link.objects.filter(owner=info.context.user).values()
        # print(owner_links)
        # iterate through the list to check each value
        for owner in owner_links:
            # first we extract the owner as a list
            owner = list(owner.values())
            # the owner is the last value in the list
            owned_id = (owner[0])

            print([owned_id, int(id)])
            # create a list to store the values of the id in the list of owned ids and the id passed in
            is_owner = [owned_id, int(id)]
            # compare the id of the owned links to the id passed in and if the user is logged in
            if (is_owner[0] == is_owner[1]) and user.is_authenticated:
                link = Link(id=id)
                link.delete()

                return DeleteLink(
                    id=link.id      
                )
        raise Exception('Not authorized to delete this link. Please sign in or try a different link.')


class Mutation(graphene.ObjectType):
    create_link = CreateLink.Field()
    update_link = UpdateLink.Field()
    delete_link = DeleteLink.Field() 