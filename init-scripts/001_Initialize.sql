create table if not exists public."Characters" (
    "Id" uuid not null,
    "Name" text not null,
    "Elo" double precision not null,
    constraint "PK_Characters" primary key ("Id")
);

create table if not exists public."Cards"(
    "Id" uuid not null,
    "ObjectKey" text not null,
    "CreatedAt" timestamptz not null,
    constraint "PK_Card" primary key ("Id")
);

create table if not exists public."CharacterCards" (
    "Id" uuid not null,
    "CardId" uuid not null,
    "CharacterId" uuid not null,
    constraint "PK_CharacterCard" primary key ("Id"),
    constraint "FK_CharacterCards_Cards" foreign key ("CardId")
            references public."Cards" ("Id") on delete restrict,
    constraint "FK_CharacterCards_Characters" foreign key ("CharacterId")
            references public."Characters" ("Id") on delete restrict
);
