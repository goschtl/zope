
dojo.provide("zc.dozodb.tests");

dojo.registerModulePath('zc', '../../../src/zc/dozodb');

dojo.require("zc.dozodb");

doh.register("MyTests", [
  function assertTrueTest(){
    doh.assertTrue(true);
    doh.assertTrue(1);
    doh.assertTrue(!false);
  }
]);
