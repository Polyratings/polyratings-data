require("reflect-metadata");
const fs = require("fs");
const fetch = require("node-fetch");
const { plainToInstance, instanceToPlain } = require("class-transformer");
const { Client, PROD_ENV, Internal } = require("@polyratings/client");

global.fetch = fetch;

async function main() {
  const client = new Client(PROD_ENV);
  await client.auth.login({
    username: process.env.POLYRATINGS_USERNAME,
    password: process.env.POLYRATINGS_PASSWORD,
  });

  const allProfessors = await client.admin.bulkKvRecord("professors");
  // delete all professor key to generate it ourselves
  delete allProfessors.all;

  const generatedAllProfessors = plainToInstance(
    Internal.TruncatedProfessorDTO,
    Object.values(allProfessors),
    { excludeExtraneousValues: true }
  );
  const generatedAllProfessorsPlain = instanceToPlain(generatedAllProfessors);
  fs.writeFileSync(
    "professor-list.json",
    JSON.stringify(generatedAllProfessorsPlain, null, 2)
  );

  fs.writeFileSync(
    "professor-dump.json",
    JSON.stringify(Object.values(allProfessors), null, 2)
  );
}
main();
