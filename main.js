const fs = require("fs");
const fetch = require("node-fetch")
const { Client, PROD_ENV } = require("@polyratings/client");

global.fetch = fetch

async function main() {
  const client = new Client(PROD_ENV);
  await client.auth.login({
    username: process.env.POLYRATINGS_USERNAME,
    password: process.env.POLYRATINGS_PASSWORD,
  });
  const allProfessors = await client.admin.bulkKvRecord("professors");

  fs.writeFileSync(
    "professor-list.json",
    JSON.stringify(allProfessors.all, null, 2)
  );
  delete allProfessors.all;

  fs.writeFileSync(
    "professor-dump.json",
    JSON.stringify(Object.values(allProfessors), null, 2)
  );
}
main();
