create table public."Anime" (
    "Id" uuid not null primary key,
    "Name" text not null
);

create table public."Characters" (
    "Id" uuid not null primary key,
    "Name" text not null,
    "Elo" double precision not null default 1500,
    "BattleCount" int not null default 0,
    "AnimeId" uuid not null references public."Anime" ("Id") on delete restrict
);

create table public."Cards" (
    "Id" uuid not null primary key,
    "ObjectKey" text not null,
    "CreatedAt" timestamptz not null
);

create table public."CharacterCards" (
    "Id" uuid not null primary key,
    "CardId" uuid not null references public."Cards" ("Id") on delete restrict,
    "CharacterId" uuid not null references public."Characters" ("Id") on delete restrict
);

create table public."Battles" (
    "Id" uuid not null primary key,
    "CreatedAt" timestamptz not null,
    "ResolvedAt" timestamptz,
    "RoundCount" int not null default 0
);

create table public."BattlePools" (
    "Id" uuid not null primary key,
    "BattleId" uuid not null references public."Battles" ("Id") on delete restrict,
    "CharacterId" uuid not null references public."Characters" ("Id") on delete restrict
);

create table public."BattleMatches" (
    "Id" uuid not null primary key,
    "BattleId" uuid not null references public."Battles" ("Id") on delete restrict,
    "Round" int not null,
    "WinnerId" uuid not null references public."Characters" ("Id") on delete restrict,
    "LoserId" uuid not null references public."Characters" ("Id") on delete restrict,
    "CreatedAt" timestamptz not null
);
