class Header extends React.Component {
  render() {
    const e = React.createElement;

    return (
      e(
        'div', {	className: 'header' },
        e(
          "div", { className: "header-container" },
          e(
            'div', { className: "header-left-element" },
            e('a', { href: 'https://github.com/ethereum/rig' }, "Robust Incentives Group")
          ),
          e(
            'div', { className: "header-right-elements" },
            e(
              'div', { className: "header-right-element" },
              e('a', { href: '/abm1559' }, "eip1559")
            ),
            e(
              'div', { className: "header-right-element" },
              e('a', { href: '/beaconrunner' }, "eth2")
            )
            // e(
            //   'div', { className: "header-right-element" },
            //   e('a', { href: '/about' }, 'About')
            // ),
            // e(
            //   'div', { className: "header-right-element" },
            //   e('a', { href: 'https://twitter.com/hackingresearch' }, 'Twitter')
            // )
          )
        )
      )
    );
  }
}
